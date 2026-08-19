from qdrant_client import QdrantClient

client = QdrantClient("localhost", port=6333)

# Collection info
info = client.get_collection("ledra_brands_products_xlsx")
print(f"Collection: ledra_brands_products_xlsx")
print(f"Vector count: {info.points_count}")
print(f"Vector size: {info.config.params.vectors.size}")
print(f"Distance: {info.config.params.vectors.distance}")
print("\n" + "="*60 + "\n")

# Scroll first 20 vectors
results, _ = client.scroll(
    collection_name="ledra_brands_products_xlsx",
    limit=20,
    with_payload=True,
    with_vectors=False
)

for r in results:
    print(f"--- ID: {r.id} ---")
    for key, value in r.payload.items():
        preview = str(value)[:200] + "..." if len(str(value)) > 200 else value
        print(f"  {key}: {preview}")
    print()