#!/usr/bin/env python3
"""
Script to inspect the contents of the FAISS vector database.
Run from the backend directory: python inspect_vector_db.py
"""
import sys
import os
from collections import defaultdict
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.vector_db import get_vector_db
from app.config import settings


def format_text(text, max_length=200):
    """Truncate text for display"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def inspect_vector_db():
    """Inspect and display vector database contents"""
    print("=" * 80)
    print("Vector Database Inspector")
    print("=" * 80)
    print()
    
    # Load vector database
    print(f"Loading vector database from: {settings.vector_db_path}")
    vector_db = get_vector_db(
        index_path=settings.vector_db_path,
        dimension=settings.embedding_dimension
    )
    
    # Check if index exists
    if vector_db.index is None or vector_db.index.ntotal == 0:
        print("\n[WARNING] Vector database is empty or not found!")
        print(f"   Index path: {settings.vector_db_path}")
        if not os.path.exists(settings.vector_db_path):
            print(f"   File does not exist.")
        return
    
    # Get statistics
    total_vectors = vector_db.index.ntotal
    total_metadata = len(vector_db.metadata)
    
    print(f"[OK] Loaded successfully!")
    print()
    print("=" * 80)
    print("STATISTICS")
    print("=" * 80)
    print(f"Total vectors in index: {total_vectors}")
    print(f"Total metadata entries: {total_metadata}")
    print(f"Embedding dimension: {settings.embedding_dimension}")
    print()
    
    # Group by paper_id
    papers = defaultdict(lambda: {"chunks": [], "pages": set()})
    
    for faiss_id, metadata in vector_db.metadata.items():
        paper_id = metadata.get("paper_id", "unknown")
        papers[paper_id]["chunks"].append(metadata)
        if "page_number" in metadata:
            papers[paper_id]["pages"].add(metadata["page_number"])
    
    print("=" * 80)
    print(f"PAPERS IN DATABASE ({len(papers)} total)")
    print("=" * 80)
    print()
    
    for i, (paper_id, data) in enumerate(sorted(papers.items()), 1):
        num_chunks = len(data["chunks"])
        pages = sorted(data["pages"])
        print(f"{i}. Paper ID: {paper_id}")
        print(f"   Chunks: {num_chunks}")
        if pages:
            print(f"   Pages: {len(pages)} (pages {min(pages)} to {max(pages)})")
        else:
            print(f"   Pages: N/A")
        print()
    
    # Show sample chunks
    print("=" * 80)
    print("SAMPLE CHUNKS (first 5 chunks from first paper)")
    print("=" * 80)
    print()
    
    if papers:
        first_paper_id = sorted(papers.keys())[0]
        chunks = sorted(papers[first_paper_id]["chunks"], 
                       key=lambda x: (x.get("page_number", 0), x.get("chunk_index", 0)))
        
        for i, chunk in enumerate(chunks[:5], 1):
            print(f"Chunk {i}:")
            print(f"  Paper ID: {chunk.get('paper_id', 'N/A')}")
            print(f"  Page: {chunk.get('page_number', 'N/A')}")
            print(f"  Chunk Index: {chunk.get('chunk_index', 'N/A')}")
            print(f"  Text Preview: {format_text(chunk.get('text', 'N/A'), 150)}")
            print()
    
    # Show detailed breakdown
    print("=" * 80)
    print("DETAILED BREAKDOWN BY PAPER")
    print("=" * 80)
    print()
    
    for paper_id, data in sorted(papers.items()):
        chunks = data["chunks"]
        pages = sorted(data["pages"])
        
        # Count chunks per page
        chunks_per_page = defaultdict(int)
        for chunk in chunks:
            page = chunk.get("page_number", "unknown")
            chunks_per_page[page] += 1
        
        print(f"Paper: {paper_id}")
        print(f"  Total chunks: {len(chunks)}")
        print(f"  Pages covered: {len(pages)}")
        print(f"  Chunks per page:")
        for page in sorted(chunks_per_page.keys()):
            print(f"    Page {page}: {chunks_per_page[page]} chunks")
        print()


if __name__ == "__main__":
    try:
        inspect_vector_db()
    except Exception as e:
        print(f"\n[ERROR] Error: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
