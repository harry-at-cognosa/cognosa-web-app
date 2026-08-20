# Taking the Cognosa GitHub repo private

Status (2026-08-20): **deferred**. Repo remains public for now. Revisit after the
EC2 dev/demo instances have deploy keys in place.

## Constraints on a free GitHub account

- Free plan allows unlimited collaborators on private repos; cost is not a factor.
- Human access is per-GitHub-account only: Settings → Collaborators → invite by
  username or email. The invitee must have a GitHub account. There is no
  repo-scoped share link or token that grants a person access without one.
- Private-repo features gated behind GitHub Pro (lost on Free once private):
  branch protection rules, required reviewers, CODEOWNERS enforcement, wikis,
  GitHub Pages.

## Repo-specific credentials (for machines, not people)

1. **Deploy key** — Settings → Deploy keys. An SSH public key attached to one
   repo, read-only or read/write, no expiry, not tied to a user account. A given
   key can be registered to only one repo, but any number of distinct keys can
   be on the same repo: each EC2 instance generates its own keypair and both are
   added. Preferred mechanism for `git pull` on the dev and demo servers.
2. **Fine-grained personal access token** — Settings → Developer settings.
   Scoped to selected repos with per-permission grants (e.g. `Contents: read`).
   Works over HTTPS via a credential helper. Acts as the issuing user and has an
   expiry that must be rotated.
3. **GitHub App installation token** — overkill for this use.

GitLab equivalent (second remote): a project **Deploy Token** with
`read_repository`, which is the closest thing to a true repo-specific token.

## Recommended approach

- Make the repo private.
- Add collaborators by GitHub account for humans.
- Put a read-only deploy key on each EC2 instance. This dovetails with the
  git-pull-based deploy revamp: the server clones over SSH with its deploy key
  and a deploy becomes `git fetch && git checkout <tag>` plus migrations, with
  no copy step.

## Pre-flip checklist

- Identify anything fetching the repo anonymously — pip installs from a git
  URL, CI jobs, `curl raw.githubusercontent.com` in setup scripts. These break
  the moment the repo goes private.
- Confirm no reliance on Pro-only features listed above.
- Generate and register a deploy key per EC2 instance; verify `git fetch` over
  SSH from each before flipping visibility.
