#!/usr/bin/env python3
"""Interactive Casambi collection query tester."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from common.parsed_url import ParsedUrl
from tasks_lib.vdb_lib.qdrant_ops import QdrantOps
from tasks_lib.vdb_lib.emb_models import HuggingFaceEmbeddings
from collections import Counter

# Configuration
QDRANT_URL = "localhost:6333"
COLLECTION_NAME = "casambi_collection"
TRANSFORMER_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def interactive_query_test():
    """Interactive query testing for Casambi collection."""
    
    # Initialize
    qdrant_ops = QdrantOps(ParsedUrl.from_url(QDRANT_URL))
    
    if not qdrant_ops.collection_exists(COLLECTION_NAME):
        print(f"❌ Collection {COLLECTION_NAME} not found!")
        return
    
    emb_obj = HuggingFaceEmbeddings(model_name=TRANSFORMER_MODEL)
    
    # Retrieval configurations
    configs = {
        "1": {"name": "Similarity", "config": {"search_type": "similarity", "search_kwargs": {"k": 5}}},
        "2": {"name": "MMR (diverse)", "config": {"search_type": "mmr", "search_kwargs": {"k": 5, "fetch_k": 10}}},
        "3": {"name": "Threshold", "config": {"search_type": "similarity_score_threshold", "search_kwargs": {"score_threshold": 0.5, "k": 5}}}
    }
    
    # Default to similarity
    current_config = configs["1"]["config"]
    current_config_name = configs["1"]["name"]
    
    print("\n🔍 CASAMBI COLLECTION QUERY TESTER")
    print("="*60)
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Ready for queries!\n")
    print("Commands:")
    print("  'quit' or 'exit' - Exit the program")
    print("  'config' - Change retrieval method")
    print("  'stats' - Show collection statistics")
    print("  'help' - Show sample queries")
    print("-"*60)
    
    while True:
        print(f"\n[{current_config_name}] Enter query (or command): ")
        query = input("> ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
            
        elif query.lower() == 'config':
            print("\nSelect retrieval method:")
            for key, value in configs.items():
                print(f"  {key}: {value['name']}")
            choice = input("Choice (1-3): ").strip()
            if choice in configs:
                current_config = configs[choice]["config"]
                current_config_name = configs[choice]["name"]
                print(f"✅ Switched to {current_config_name}")
            else:
                print("Invalid choice")
            continue
            
        elif query.lower() == 'stats':
            show_statistics(qdrant_ops, emb_obj)
            continue
            
        elif query.lower() == 'help':
            print("\nSample queries to try:")
            print("  - How to create a scene?")
            print("  - What are the benefits for hotels?")
            print("  - Security features")
            print("  - Quick reference for retail")
            print("  - iBeacon configuration")
            print("  - Energy efficiency guidelines")
            continue
            
        elif not query:
            continue
        
        # Process the query
        print(f"\nSearching for: '{query}'")
        print("-"*60)
        
        try:
            docs = qdrant_ops.get_docs(
                emb_obj=emb_obj,
                collection_name=COLLECTION_NAME,
                query_text=query,
                gvdbs_cfg_json=current_config
            )
            
            if docs:
                print(f"Found {len(docs)} results:\n")
                
                for i, doc in enumerate(docs, 1):
                    metadata = doc.get('metadata', {})
                    
                    print(f"Result {i}:")
                    print(f"  📄 File: {metadata.get('source_file', 'unknown')}")
                    print(f"  📁 Folder: {metadata.get('folder_structure', 'unknown')}")
                    print(f"  🏷️  Type: {metadata.get('doc_type', 'unknown')}")
                    print(f"  🔧 Strategy: {metadata.get('chunking_strategy', 'unknown')}")
                    print(f"  📍 Chunk: {metadata.get('chunk_index', '?')}/{metadata.get('total_chunks', '?')}")
                    
                    # Content preview
                    content = doc.get('page_content', doc.get('text', ''))
                    if content:
                        preview = content[:200].replace('\n', ' ')
                        print(f"  📝 Content: {preview}...")
                    print()
                    
                    # Ask if user wants to see more after first 3
                    if i == 3 and len(docs) > 3:
                        more = input(f"Show remaining {len(docs)-3} results? (y/n): ")
                        if more.lower() != 'y':
                            break
            else:
                print("❌ No results found")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def show_statistics(qdrant_ops, emb_obj):
    """Show collection statistics."""
    print("\n📊 COLLECTION STATISTICS")
    print("="*60)
    
    # Get a sample of documents to analyze
    sample_query = "Casambi"  # Generic query to get diverse results
    
    try:
        docs = qdrant_ops.get_docs(
            emb_obj=emb_obj,
            collection_name=COLLECTION_NAME,
            query_text=sample_query,
            gvdbs_cfg_json={"search_type": "similarity", "search_kwargs": {"k": 50}}
        )
        
        if docs:
            doc_types = Counter()
            strategies = Counter()
            sources = Counter()
            folders = Counter()
            
            for doc in docs:
                metadata = doc.get('metadata', {})
                doc_types[metadata.get('doc_type', 'unknown')] += 1
                strategies[metadata.get('chunking_strategy', 'unknown')] += 1
                sources[metadata.get('source_file', 'unknown')] += 1
                folders[metadata.get('folder_structure', 'unknown')] += 1
            
            print("\nDocument Types in sample:")
            for dtype, count in doc_types.most_common():
                print(f"  {dtype}: {count}")
            
            print("\nChunking Strategies:")
            for strategy, count in strategies.most_common():
                print(f"  {strategy}: {count}")
            
            print("\nTop Source Files:")
            for source, count in sources.most_common(5):
                print(f"  {source}: {count}")
            
            print("\nFolder Structure:")
            for folder, count in folders.most_common():
                print(f"  {folder}: {count}")
    except Exception as e:
        print(f"Error getting statistics: {e}")

if __name__ == "__main__":
    interactive_query_test()