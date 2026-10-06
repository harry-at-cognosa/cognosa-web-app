#!/usr/bin/env bash
#
# publish_s3.sh — publish the architecture diagram pages to https://files.cognosa.net/
#
# WHAT IT DOES
#   1. Regenerates each diagram page from its generator (unless --no-gen).
#   2. Wraps each generated page in a full HTML skeleton. The committed
#      cognosa_*.html files have no <!doctype>, <html>, <head> or <body> because the
#      claude.ai Artifact viewer adds those itself; a browser loading the file straight
#      from S3 needs them (charset, viewport, title, color-scheme hint).
#   3. Uploads the wrapped files to the bucket root with an explicit HTML content type.
#      Without --content-type S3 stores "binary/octet-stream" and browsers download the
#      file instead of rendering it (see ~/0_playbooks/canonical/infrastructure.md, "S3").
#   4. Invalidates the published paths on the CloudFront distribution that fronts
#      files.cognosa.net, so the new versions appear within a minute or two rather
#      than after the 5-minute cache-control expires.
#   5. Fetches each public URL and prints the HTTP status, content type and size.
#
# PUBLISHED NAMES (bucket root; the public URL is https://files.cognosa.net/<name>)
#   deployment_topology/cognosa_deployment_topology.html -> Cognosa_deployment_topology.html
#   component_stack/cognosa_component_stack.html         -> Cognosa_component_stack.html
#   query_sequence/cognosa_query_sequence.html           -> Cognosa_query_sequence.html
#   platform_overview/cognosa_platform_overview.html     -> Cognosa_platform_overview.html
#
# USAGE
#   docs/architecture/publish_s3.sh            # regenerate, wrap, upload all three, invalidate, verify
#   docs/architecture/publish_s3.sh --no-gen   # skip the generators; publish the committed HTML as is
#   docs/architecture/publish_s3.sh --dry-run  # do everything except the upload and invalidation
#   docs/architecture/publish_s3.sh component_stack   # only the named diagram folder(s)
#
# REQUIREMENTS
#   - AWS CLI configured as IAM user hal2019 (account 033684811905). Check with:
#       aws sts get-caller-identity
#   - python3 on PATH (the generators are plain Python, no third-party packages).
#   - curl for the verification step.
#
# INFRASTRUCTURE FACTS (from ~/0_playbooks/canonical/infrastructure.md)
#   Bucket:        files.cognosa.net, us-east-1, static website hosting, public read
#   CloudFront:    EAZCV38S6H0ST, alias files.cognosa.net, HTTPS via the *.cognosa.net ACM cert
#   Cache policy:  objects are uploaded with "public, max-age=300"
#
# This script never deletes anything. Re-running it overwrites the keys above and
# nothing else. The private claude.ai artifact copies are separate and are republished
# from a Claude Code session, not by this script.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUCKET="files.cognosa.net"
DISTRIBUTION_ID="EAZCV38S6H0ST"
CACHE_CONTROL="public, max-age=300"
CONTENT_TYPE="text/html; charset=utf-8"

# folder -> generator -> committed page -> published name
declare -a ALL=(
  "deployment_topology|gen_deployment_topology.py|cognosa_deployment_topology.html|Cognosa_deployment_topology.html"
  "component_stack|gen_component_stack.py|cognosa_component_stack.html|Cognosa_component_stack.html"
  "query_sequence|gen_query_sequence.py|cognosa_query_sequence.html|Cognosa_query_sequence.html"
  "platform_overview|gen_platform_overview.py|cognosa_platform_overview.html|Cognosa_platform_overview.html"
)

GEN=1; DRY=0; SELECT=()
for arg in "$@"; do
  case "$arg" in
    --no-gen)  GEN=0 ;;
    --dry-run) DRY=1 ;;
    -h|--help) sed -n '2,45p' "$0"; exit 0 ;;
    *)         SELECT+=("$arg") ;;
  esac
done

# pick the rows whose folder was named on the command line (or all of them)
ROWS=()
for row in "${ALL[@]}"; do
  folder="${row%%|*}"
  if [ ${#SELECT[@]} -eq 0 ]; then ROWS+=("$row"); else
    for s in "${SELECT[@]}"; do [ "$s" = "$folder" ] && ROWS+=("$row"); done
  fi
done
[ ${#ROWS[@]} -gt 0 ] || { echo "no matching diagram folder; choose from: deployment_topology component_stack query_sequence platform_overview" >&2; exit 1; }

command -v aws >/dev/null || { echo "aws CLI not found" >&2; exit 1; }
command -v python3 >/dev/null || { echo "python3 not found" >&2; exit 1; }
echo "AWS identity: $(aws sts get-caller-identity --query Arn --output text)"

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

wrap_page () {
  # $1 = committed page (no skeleton), $2 = output path with skeleton
  local src="$1" dst="$2" title
  title="$(grep -o '<title>[^<]*</title>' "$src" | head -1)"
  {
    printf '<!doctype html>\n<html lang="en">\n<head>\n'
    printf '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    printf '%s\n' "$title"
    printf '<style>html{color-scheme:light dark}body{margin:0}img{max-width:100%%}</style>\n'
    printf '</head>\n<body>\n'
    sed '/<title>[^<]*<\/title>/d' "$src"        # the page's own <title> moved into <head> above
    printf '\n</body>\n</html>\n'
  } > "$dst"
}

PATHS=()
for row in "${ROWS[@]}"; do
  IFS='|' read -r folder gen page name <<< "$row"
  if [ "$GEN" -eq 1 ]; then
    echo "generating  $folder/$page"
    (cd "$HERE/$folder" && python3 "$gen" >/dev/null)
  fi
  wrap_page "$HERE/$folder/$page" "$WORK/$name"
  echo "wrapped     $name ($(wc -c < "$WORK/$name" | tr -d ' ') bytes)"
  if [ "$DRY" -eq 0 ]; then
    aws s3 cp "$WORK/$name" "s3://$BUCKET/$name" \
      --content-type "$CONTENT_TYPE" --cache-control "$CACHE_CONTROL" --only-show-errors
    echo "uploaded    s3://$BUCKET/$name"
  else
    echo "dry-run     would upload s3://$BUCKET/$name"
  fi
  PATHS+=("/$name")
done

if [ "$DRY" -eq 0 ]; then
  inv="$(aws cloudfront create-invalidation --distribution-id "$DISTRIBUTION_ID" \
          --paths "${PATHS[@]}" --query 'Invalidation.Id' --output text)"
  echo "invalidated $DISTRIBUTION_ID ${PATHS[*]} (id $inv)"
  echo
  echo "verifying (the CDN may still serve the old copy for a minute or two):"
  for p in "${PATHS[@]}"; do
    printf '  https://%s%s  ' "$BUCKET" "$p"
    curl -sS -o /dev/null -w '%{http_code} %{content_type} %{size_download}B\n' "https://$BUCKET$p"
  done
else
  echo "dry-run     would invalidate $DISTRIBUTION_ID ${PATHS[*]}"
fi
