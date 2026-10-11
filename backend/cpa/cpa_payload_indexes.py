"""
Create the keyword payload indexes cpa-c42t_collection relies on for batch
rollback and per-file queries. Idempotent: re-running is harmless.

    python cpa/cpa_payload_indexes.py [--host H --port P --collection C]

PLAN-batch-refresh_261011.md section 4.4.
"""
import argparse
from qdrant_client import QdrantClient
from qdrant_client.models import PayloadSchemaType

FIELDS = ['metadata.cpa_batch', 'metadata.cpa_source_file']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--collection', default='cpa-c42t_collection')
    ap.add_argument('--host', default='localhost')
    ap.add_argument('--port', type=int, default=6333)
    args = ap.parse_args()

    client = QdrantClient(host=args.host, port=args.port)
    have = client.get_collection(args.collection).payload_schema or {}
    for field in FIELDS:
        if field in have:
            print(f"exists  {field}  ({have[field].data_type})")
            continue
        client.create_payload_index(args.collection, field_name=field,
                                    field_schema=PayloadSchemaType.KEYWORD, wait=True)
        print(f"created {field}  keyword")
    schema = client.get_collection(args.collection).payload_schema or {}
    print(f"payload_schema now: {sorted(schema)}")


if __name__ == '__main__':
    main()
