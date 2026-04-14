"""
Initialize or rebuild the RAG index for disaster protocols.
Run this script whenever you add or update documents in the data folder.
"""

from tools.rag_system import DisasterProtocolRAG


def main():
    print("=" * 60)
    print("Disaster Protocol RAG Index Builder")
    print("=" * 60)
    print()
    
    rag = DisasterProtocolRAG(data_dir="data", index_path="data/faiss_index")
    
    print("This will scan all PDF files in the data folder,")
    print("chunk them, create embeddings, and build a FAISS index.")
    print()
    
    try:
        rag.build_index()
        print()
        print("✓ RAG index built successfully!")
        print(f"✓ Indexed {len(rag.documents)} document chunks")
        print(f"✓ Index saved to: {rag.index_path}")
        print()
        print("The intelligence agent can now search these protocols.")
        
    except Exception as e:
        print(f"✗ Error building index: {e}")
        print()
        print("Make sure you have installed the required packages:")
        print("  pip install -r requirements.txt")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
