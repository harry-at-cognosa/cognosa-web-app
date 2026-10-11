"""
Remove every point one batch added to cpa-c42t_collection.

    python cpa/cpa_batch_rollback.py --batch 261011 [--dry-run]

Safe because the loader never overwrites an existing point (it skips IDs that
are already present), so a batch owns exactly the points carrying its label.

PLAN-batch-refresh_261011.md section 4.5.
"""
import argparse
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, FilterSelector


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--batch', required=True)
    ap.add_argument('--collection', default='cpa-c42t_collection')
    ap.add_argument('--host', default='localhost')
    ap.add_argument('--port', type=int, default=6333)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    client = QdrantClient(host=args.host, port=args.port)
    flt = Filter(must=[FieldCondition(key='metadata.cpa_batch', match=MatchValue(value=args.batch))])
    before = client.get_collection(args.collection).points_count
    n = client.count(args.collection, count_filter=flt, exact=True).count
    print(f"collection {args.collection}: {before:,} points, {n:,} carry cpa_batch={args.batch}")
    if args.dry_run or n == 0:
        print("nothing deleted")
        return
    client.delete(args.collection, points_selector=FilterSelector(filter=flt), wait=True)
    after = client.get_collection(args.collection).points_count
    print(f"deleted {before - after:,}; collection now {after:,} points")


if __name__ == '__main__':
    main()
