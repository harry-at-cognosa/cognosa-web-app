#!/usr/bin/env python3
"""Interactive Casambi collection query tester v2 - Enhanced display with word/char counts."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from common.parsed_url import ParsedUrl
from tasks_lib.vdb_lib.qdrant_ops import QdrantOps
from tasks_lib.vdb_lib.emb_models import HuggingFaceEmbeddings
from collections import Counter
from datetime import datetime

# Configuration
QDRANT_URL = "localhost:6333"
COLLECTION_NAME = "casambi_collection"
TRANSFORMER_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Display configuration
PREVIEW_LENGTH = 250  # Characters to show in preview
SHOW_DETAILED_STATS = True  # Show word/char counts

def interactive_query_test():
    """Interactive query testing for Casambi collection with enhanced display."""
    
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
        "3": {"name": "Threshold", "config": {"search_type": "similarity_score_threshold", "search_kwargs": {"score_threshold": 0.5, "k": 5}}},
        "4": {"name": "More results", "config": {"search_type": "similarity", "search_kwargs": {"k": 10}}},
    }
    
    # Default to similarity
    current_config = configs["1"]["config"]
    current_config_name = configs["1"]["name"]
    
    # Session tracking
    session_start = datetime.now()
    query_count = 0
    query_history = []
    
    print("\n🔍 CASAMBI COLLECTION QUERY TESTER v2")
    print("="*70)
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Session started: {session_start.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Ready for queries!\n")
    print("Commands:")
    print("  'quit' or 'exit' - Exit the program")
    print("  'config' - Change retrieval method")
    print("  'stats' - Show collection statistics")
    print("  'history' - Show query history")
    print("  'detail' - Toggle detailed view on/off")
    print("  'help' - Show sample queries")
    print("-"*70)
    
    # Display mode
    detailed_view = True
    
    while True:
        print(f"\n[{current_config_name}] Enter query (or command): ")
        query = input("> ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print(f"\n📊 Session Summary:")
            print(f"  Queries run: {query_count}")
            print(f"  Duration: {datetime.now() - session_start}")
            print("Goodbye!")
            break
            
        elif query.lower() == 'config':
            print("\nSelect retrieval method:")
            for key, value in configs.items():
                print(f"  {key}: {value['name']}")
            choice = input("Choice (1-4): ").strip()
            if choice in configs:
                current_config = configs[choice]["config"]
                current_config_name = configs[choice]["name"]
                print(f"✅ Switched to {current_config_name}")
                print(f"   Settings: {current_config['search_kwargs']}")
            else:
                print("Invalid choice")
            continue
            
        elif query.lower() == 'stats':
            show_collection_statistics(qdrant_ops, emb_obj)
            continue
            
        elif query.lower() == 'history':
            show_query_history(query_history)
            continue
            
        elif query.lower() == 'detail':
            detailed_view = not detailed_view
            print(f"✅ Detailed view: {'ON' if detailed_view else 'OFF'}")
            continue
            
        elif query.lower() == 'help':
            show_help()
            continue
            
        elif not query:
            continue
        
        # Process the query
        query_count += 1
        query_history.append((query, current_config_name))
        
        print(f"\n{'='*70}")
        print(f"🔍 Query #{query_count}: '{query}'")
        print(f"📋 Method: {current_config_name}")
        print('='*70)
        
        try:
            start_time = datetime.now()
            docs = qdrant_ops.get_docs(
                emb_obj=emb_obj,
                collection_name=COLLECTION_NAME,
                query_text=query,
                gvdbs_cfg_json=current_config
            )
            retrieval_time = (datetime.now() - start_time).total_seconds()
            
            if docs:
                print(f"⏱️  Retrieved {len(docs)} results in {retrieval_time:.2f} seconds\n")
                
                # Track statistics for this query
                doc_types = Counter()
                strategies = Counter()
                
                for i, doc in enumerate(docs, 1):
                    metadata = doc.get('metadata', {})
                    
                    # Extract all metadata fields
                    doc_type = metadata.get('doc_type', 'unknown')
                    strategy = metadata.get('chunking_strategy', 'default/unknown')
                    source_file = metadata.get('source_file', 'unknown')
                    folder = metadata.get('folder_structure', 'unknown')
                    chunk_idx = metadata.get('chunk_index', '?')
                    total_chunks = metadata.get('total_chunks', '?')
                    confidence = metadata.get('classification_confidence', 0)
                    method = metadata.get('classification_method', 'unknown')
                    
                    # Track stats
                    doc_types[doc_type] += 1
                    strategies[strategy] += 1
                    
                    # Get content and calculate sizes
                    content = doc.get('page_content', doc.get('text', ''))
                    word_count = len(content.split()) if content else 0
                    char_count = len(content) if content else 0
                    
                    print(f"─── Result {i} {'─'*55}")
                    print(f"  📄 File: {source_file}")
                    print(f"  📁 Folder: {folder}")
                    print(f"  🏷️  Type: {doc_type} (confidence: {confidence:.2f}, method: {method})")
                    print(f"  🔧 Strategy: {strategy}")
                    print(f"  📍 Chunk: {chunk_idx}/{total_chunks} from this document")
                    print(f"  📏 Size: {word_count} words, {char_count} characters")
                    
                    if detailed_view and content:
                        # Show more content in detailed view
                        preview_length = PREVIEW_LENGTH if not detailed_view else 350
                        preview = content[:preview_length].replace('\n', ' ')
                        
                        # Add ellipsis if truncated
                        if len(content) > preview_length:
                            preview += "..."
                            
                        print(f"  📝 Content preview ({preview_length}/{char_count} chars shown):")
                        
                        # Word wrap the preview for better readability
                        wrapped_preview = word_wrap(preview, width=65, indent=5)
                        print(wrapped_preview)
                    elif content:
                        # Short preview in non-detailed view
                        preview = content[:150].replace('\n', ' ')
                        if len(content) > 150:
                            preview += "..."
                        print(f"  📝 Preview: {preview}")
                    
                    print()
                    
                    # Ask if user wants to see more after first 3 in non-detailed view
                    if not detailed_view and i == 3 and len(docs) > 3:
                        remaining = len(docs) - 3
                        more = input(f"  Show remaining {remaining} results? (y/n): ")
                        if more.lower() != 'y':
                            break
                    
                    # In detailed view, paginate every 5 results
                    if detailed_view and i % 5 == 0 and i < len(docs):
                        remaining = len(docs) - i
                        more = input(f"  Continue with {remaining} more results? (y/n): ")
                        if more.lower() != 'y':
                            break
                
                # Show query statistics
                print(f"\n📊 Query Statistics:")
                print(f"  Document types retrieved: {', '.join(f'{t}({c})' for t, c in doc_types.items())}")
                print(f"  Chunking strategies: {', '.join(f'{s}({c})' for s, c in strategies.items())}")
                
            else:
                print("❌ No results found")
                print("   Try:")
                print("   - Using different keywords")
                print("   - Switching to 'config' option 3 (threshold) with lower threshold")
                print("   - Checking 'stats' to see what's in the collection")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            if detailed_view:
                traceback.print_exc()

def word_wrap(text, width=70, indent=0):
    """Simple word wrapping for better display."""
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 > width:
            lines.append(' ' * indent + ' '.join(current_line))
            current_line = [word]
            current_length = len(word)
        else:
            current_line.append(word)
            current_length += len(word) + 1
    
    if current_line:
        lines.append(' ' * indent + ' '.join(current_line))
    
    return '\n'.join(lines)

def show_collection_statistics(qdrant_ops, emb_obj):
    """Show detailed collection statistics."""
    print("\n" + "="*70)
    print("📊 COLLECTION STATISTICS")
    print("="*70)
    
    # Get a sample of documents to analyze
    sample_query = "Casambi"  # Generic query to get diverse results
    
    try:
        docs = qdrant_ops.get_docs(
            emb_obj=emb_obj,
            collection_name=COLLECTION_NAME,
            query_text=sample_query,
            gvdbs_cfg_json={"search_type": "similarity", "search_kwargs": {"k": 100}}
        )
        
        if docs:
            doc_types = Counter()
            strategies = Counter()
            sources = Counter()
            folders = Counter()
            total_words = 0
            total_chars = 0
            chunk_sizes = []
            
            for doc in docs:
                metadata = doc.get('metadata', {})
                doc_types[metadata.get('doc_type', 'unknown')] += 1
                strategies[metadata.get('chunking_strategy', 'unknown')] += 1
                sources[metadata.get('source_file', 'unknown')] += 1
                folders[metadata.get('folder_structure', 'unknown')] += 1
                
                # Calculate sizes
                content = doc.get('page_content', doc.get('text', ''))
                if content:
                    words = len(content.split())
                    chars = len(content)
                    total_words += words
                    total_chars += chars
                    chunk_sizes.append(chars)
            
            print(f"\nSample size: {len(docs)} chunks analyzed")
            
            print("\n📑 Document Types:")
            for dtype, count in doc_types.most_common():
                print(f"  {dtype}: {count} chunks")
            
            print("\n🔧 Chunking Strategies:")
            for strategy, count in strategies.most_common():
                print(f"  {strategy}: {count} chunks")
            
            print("\n📄 Top Source Files:")
            for source, count in sources.most_common(10):
                print(f"  {source[:50]}: {count} chunks")
            
            print("\n📁 Folder Distribution:")
            for folder, count in folders.most_common():
                print(f"  /{folder}: {count} chunks")
            
            if chunk_sizes:
                avg_size = sum(chunk_sizes) / len(chunk_sizes)
                print(f"\n📏 Chunk Size Statistics:")
                print(f"  Average: {avg_size:.0f} characters")
                print(f"  Minimum: {min(chunk_sizes)} characters")
                print(f"  Maximum: {max(chunk_sizes)} characters")
                print(f"  Total words in sample: {total_words:,}")
                print(f"  Total characters in sample: {total_chars:,}")
                
    except Exception as e:
        print(f"Error getting statistics: {e}")

def show_query_history(history):
    """Show query history for the session."""
    print("\n" + "="*70)
    print("📜 QUERY HISTORY")
    print("="*70)
    
    if not history:
        print("No queries yet in this session")
    else:
        for i, (query, method) in enumerate(history, 1):
            print(f"{i:3d}. [{method}] {query}")
    print()

def show_help():
    """Show help with sample queries."""
    print("\n" + "="*70)
    print("💡 SAMPLE QUERIES TO TRY")
    print("="*70)
    
    categories = {
        "How-to Questions": [
            "How to create a scene?",
            "How to set up timers?",
            "How to configure sensors?",
            "How to add devices to network?"
        ],
        "Technical Questions": [
            "What is the maximum network size?",
            "Bluetooth mesh topology",
            "Security features",
            "Encryption methods"
        ],
        "Use Case Specific": [
            "Benefits for hotels",
            "Retail lighting control",
            "Office automation features",
            "Outdoor lighting setup"
        ],
        "Troubleshooting": [
            "Connection problems",
            "Device not responding",
            "Network issues",
            "Firmware update"
        ],
        "Quick Reference": [
            "Quick setup guide",
            "Cheat sheet for retail",
            "Fire alarm integration",
            "Keycard configuration"
        ]
    }
    
    for category, queries in categories.items():
        print(f"\n{category}:")
        for q in queries:
            print(f"  • {q}")
    
    print("\n💡 Tips:")
    print("  • Use 'config' to try different retrieval methods")
    print("  • MMR gives more diverse results")
    print("  • Threshold filters by relevance score")
    print("  • Use 'detail' to toggle between brief and detailed views")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("CASAMBI COLLECTION INTERACTIVE QUERY TESTER v2")
    print("="*70)
    interactive_query_test()
