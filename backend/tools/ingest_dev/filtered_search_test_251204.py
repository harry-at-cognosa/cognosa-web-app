from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer

client = QdrantClient("localhost", port=6333)
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

COLLECTION = "ledra_brands_products_xlsx"

def search_filtered(query_text, filters=None, limit=5):
    """Search with optional filters, show results."""
    query_vector = model.encode(query_text).tolist()
    
    results = client.search(
        collection_name=COLLECTION,
        query_vector=query_vector,
        query_filter=filters,
        limit=limit,
        with_payload=True
    )
    return results

def print_results(results, label):
    print(f"\n{'='*60}")
    print(f"{label}")
    print(f"{'='*60}")
    for i, r in enumerate(results, 1):
        meta = r.payload.get("metadata", {})
        content = r.payload.get("page_content", "")[:150]
        print(f"\n[{i}] Score: {r.score:.4f}")
        print(f"    Product: {meta.get('product_name')} (ID: {meta.get('base_product_id')})")
        print(f"    Chunk type: {meta.get('chunk_type')}")
        if meta.get('option_name'):
            print(f"    Option: {meta.get('option_name')}")
        print(f"    Content: {content}...")


# --- QUERY 1: Pure semantic search (no filter) ---
results = search_filtered("ELV dimming options")
print_results(results, "QUERY 1: Pure semantic - 'ELV dimming options' (no filter)")


# --- QUERY 2: Filter by category, semantic search within ---
filters = Filter(must=[
    FieldCondition(key="metadata.category", match=MatchValue(value="downlights"))
])
results = search_filtered("adjustable trim", filters=filters)
print_results(results, "QUERY 2: Category=downlights, search 'adjustable trim'")


# --- QUERY 3: Filter by specific product ID, get all chunks ---
filters = Filter(must=[
    FieldCondition(key="metadata.base_product_id", match=MatchValue(value="100372"))
])
results = search_filtered("", filters=filters, limit=20)  # empty query, just retrieve
print_results(results, "QUERY 3: All chunks for product ID 100372")


# --- QUERY 4: Filter by product ID + option name ---
filters = Filter(must=[
    FieldCondition(key="metadata.base_product_id", match=MatchValue(value="100372")),
    FieldCondition(key="metadata.option_name", match=MatchValue(value="Finish"))
])
results = search_filtered("", filters=filters)
print_results(results, "QUERY 4: Product 100372, Finish options only")


# --- QUERY 5: Filter by chunk_type, semantic search ---
filters = Filter(must=[
    FieldCondition(key="metadata.chunk_type", match=MatchValue(value="base_descriptive"))
])
results = search_filtered("surface mount junction box", filters=filters)
print_results(results, "QUERY 5: Descriptive chunks, search 'surface mount junction box'")


# --- QUERY 6: Filter by brand ---
filters = Filter(must=[
    FieldCondition(key="metadata.brand", match=MatchValue(value="Bruck"))
])
results = search_filtered("track lighting", filters=filters)
print_results(results, "QUERY 6: Brand=Bruck, search 'track lighting'")