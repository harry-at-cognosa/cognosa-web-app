#!/usr/bin/env python3
"""Test Casambi collection using Cognosa's QdrantOps with proper configuration."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from common.parsed_url import ParsedUrl
from tasks_lib.vdb_lib.qdrant_ops import QdrantOps
from tasks_lib.vdb_lib.emb_models import HuggingFaceEmbeddings, EmbModels
from collections import Counter
import json

# Configuration (same as loader)
QDRANT_URL = "localhost:6333"
COLLECTION_NAME = "casambi_collection"
TRANSFORMER_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Retriever configuration (matches your platform's structure)
# These are typical LangChain retriever parameters
RETRIEVER_CONFIGS = {
    "similarity": {
        "search_type": "similarity",
        "search_kwargs": {"k": 5}
    },
    "mmr": {
        "search_type": "mmr",
        "search_kwargs": {"k": 5, "fetch_k": 10, "lambda_mult": 0.5}
    },
    "similarity_score_threshold": {
        "search_type": "similarity_score_threshold",
        "search_kwargs": {"score_threshold": 0.5, "k": 5}
    }
}

def test_casambi_retrieval():
    """Test retrieval from Casambi collection using get_docs method."""
    
    # Initialize QdrantOps
    qdrant_ops = QdrantOps(ParsedUrl.from_url(QDRANT_URL))
    
    # Check if collection exists
    if not qdrant_ops.collection_exists(COLLECTION_NAME):
        print(f"Collection {COLLECTION_NAME} not found!")
        return
    
    # Initialize embedding model
    emb_obj = HuggingFaceEmbeddings(model_name=TRANSFORMER_MODEL)
    
    print(f"Testing Casambi Collection: {COLLECTION_NAME}")
    print("="*60)
    
    # Test queries - covering different document types
    test_queries = [
        "How to create a scene in Casambi app?",  # Should match manual
        "What are the benefits of Casambi for hotels?",  # Should match hospitality use case
        "Quick setup guide for retail lighting",  # Should match cheat sheet
        "Casambi security and encryption features",  # Should match security doc
        "How to configure iBeacon",  # Should match procedural guide
        "LEED certification and energy efficiency",  # Should match sustainability
    ]
    
    # Use similarity search as default
    gvdbs_cfg = RETRIEVER_CONFIGS["similarity"]
    
    print(f"\n🔍 TESTING WITH CONFIG: {gvdbs_cfg}")
    print("\n" + "="*60 + "\n")
    
    # Track statistics
    doc_types_retrieved = Counter()
    strategies_used = Counter()
    source_files = Counter()
    
    for i, query in enumerate(test_queries, 1):
        print(f"Query {i}: '{query}'")
        print("-" * 50)
        
        try:
            # Use get_docs method with proper parameters
            docs = qdrant_ops.get_docs(
                emb_obj=emb_obj,
                collection_name=COLLECTION_NAME,
                query_text=query,
                gvdbs_cfg_json=gvdbs_cfg
            )
            
            if docs:
                print(f"Found {len(docs)} results\n")
                
                for j, doc in enumerate(docs[:3], 1):  # Show top 3
                    # Extract metadata - LangChain documents typically have metadata attribute
                    metadata = doc.get('metadata', {})
                    
                    # Extract key information
                    doc_type = metadata.get('doc_type', 'unknown')
                    source_file = metadata.get('source_file', 'unknown')
                    strategy = metadata.get('chunking_strategy', 'unknown')
                    chunk_idx = metadata.get('chunk_index', '?')
                    total_chunks = metadata.get('total_chunks', '?')
                    folder = metadata.get('folder_structure', 'unknown')
                    confidence = metadata.get('classification_confidence', 0)
                    method = metadata.get('classification_method', 'unknown')
                    
                    # Track statistics
                    doc_types_retrieved[doc_type] += 1
                    strategies_used[strategy] += 1
                    source_files[source_file] += 1
                    
                    print(f"   Result {j}:")
                    print(f"     📄 Source: {source_file}")
                    print(f"     📁 Folder: {folder}")
                    print(f"     🏷️  Type: {doc_type} (confidence: {confidence:.2f}, method: {method})")
                    print(f"     🔧 Strategy: {strategy}")
                    print(f"     📍 Chunk: {chunk_idx}/{total_chunks}")
                    
                    # Show content preview
                    content = doc.get('page_content', doc.get('text', ''))
                    if content:
                        preview = content[:150].replace('\n', ' ')
                        print(f"     📝 Preview: {preview}...")
                    
                    print()
            else:
                print("   ❌ No results found\n")
                
        except Exception as e:
            print(f"   ❌ Error during retrieval: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    # Print statistics
    print("\n" + "="*60)
    print("📊 RETRIEVAL STATISTICS")
    print("="*60)
    
    print("\n1. Document Types Retrieved:")
    for doc_type, count in doc_types_retrieved.most_common():
        print(f"   {doc_type}: {count} chunks")
    
    print("\n2. Chunking Strategies Used:")
    for strategy, count in strategies_used.most_common():
        print(f"   {strategy}: {count} chunks")
    
    print("\n3. Top Source Files:")
    for source_file, count in source_files.most_common(5):
        print(f"   {source_file}: {count} retrievals")
    
    print("\n✅ Test complete!")
    
    # Optional: Test different retrieval strategies
    print("\n" + "="*60)
    print("🧪 OPTIONAL: Test different retrieval strategies")
    print("="*60)
    
    test_query = "How to setup Casambi network"
    
    for config_name, config in RETRIEVER_CONFIGS.items():
        print(f"\n Testing {config_name}:")
        try:
            docs = qdrant_ops.get_docs(
                emb_obj=emb_obj,
                collection_name=COLLECTION_NAME,
                query_text=test_query,
                gvdbs_cfg_json=config
            )
            print(f"   Retrieved {len(docs)} documents")
        except Exception as e:
            print(f"   Error: {e}")

if __name__ == "__main__":
    test_casambi_retrieval()