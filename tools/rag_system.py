"""
Custom RAG (Retrieval-Augmented Generation) system using FAISS.
Scans documents in data folder, chunks them, and enables semantic search.
"""

import os
import pickle
from typing import List, Dict
from pathlib import Path

try:
    import faiss
    import numpy as np
    from sentence_transformers import SentenceTransformer
    import pypdf
except ImportError as e:
    print(f"Missing required packages. Install with: pip install faiss-cpu sentence-transformers pypdf")
    raise e


class DisasterProtocolRAG:
    """RAG system for disaster protocol documents."""
    
    def __init__(self, data_dir: str = "data", index_path: str = "data/faiss_index"):
        self.data_dir = Path(data_dir)
        self.index_path = Path(index_path)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.documents = []
        self.metadata = []
        
    def load_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file."""
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                text += f"\n[Page {page_num + 1}]\n{page_text}"
        return text
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks."""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
    
    def build_index(self) -> None:
        """Scan data folder, chunk documents, and build FAISS index."""
        print(f"Building RAG index from {self.data_dir}...")
        
        # Load all PDFs from data folder
        pdf_files = list(self.data_dir.glob("*.pdf"))
        
        if not pdf_files:
            print("No PDF files found in data folder.")
            return
        
        all_chunks = []
        all_metadata = []
        
        for pdf_file in pdf_files:
            print(f"Processing: {pdf_file.name}")
            text = self.load_pdf(pdf_file)
            chunks = self.chunk_text(text)
            
            for idx, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                all_metadata.append({
                    'source': pdf_file.name,
                    'chunk_id': idx,
                    'text': chunk
                })
        
        # Create embeddings
        print(f"Creating embeddings for {len(all_chunks)} chunks...")
        embeddings = self.embedding_model.encode(all_chunks, show_progress_bar=True)
        
        # Build FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(embeddings).astype('float32'))
        
        self.documents = all_chunks
        self.metadata = all_metadata
        
        # Save index
        self.save_index()
        print(f"RAG index built successfully with {len(all_chunks)} chunks.")
    
    def save_index(self) -> None:
        """Save FAISS index and metadata to disk."""
        self.index_path.mkdir(exist_ok=True)
        
        faiss.write_index(self.index, str(self.index_path / "index.faiss"))
        
        with open(self.index_path / "metadata.pkl", 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'metadata': self.metadata
            }, f)
        
        print(f"Index saved to {self.index_path}")
    
    def load_index(self) -> bool:
        """Load FAISS index from disk."""
        index_file = self.index_path / "index.faiss"
        metadata_file = self.index_path / "metadata.pkl"
        
        if not index_file.exists() or not metadata_file.exists():
            return False
        
        self.index = faiss.read_index(str(index_file))
        
        with open(metadata_file, 'rb') as f:
            data = pickle.load(f)
            self.documents = data['documents']
            self.metadata = data['metadata']
        
        return True
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search for relevant document chunks."""
        # Load index if not already loaded
        if self.index is None:
            if not self.load_index():
                print("No index found. Building new index...")
                self.build_index()
        
        # Create query embedding
        query_embedding = self.embedding_model.encode([query])
        
        # Search FAISS index
        distances, indices = self.index.search(np.array(query_embedding).astype('float32'), top_k)
        
        # Format results
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.metadata):
                result = self.metadata[idx].copy()
                result['similarity_score'] = float(1 / (1 + distance))  # Convert distance to similarity
                results.append(result)
        
        return results


# Global RAG instance
_rag_instance = None

def get_rag_instance() -> DisasterProtocolRAG:
    """Get or create global RAG instance."""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = DisasterProtocolRAG()
        # Try to load existing index, build if not found
        if not _rag_instance.load_index():
            _rag_instance.build_index()
    return _rag_instance


def search_disaster_protocols(query: str, top_k: int = 3) -> str:
    """
    Search internal disaster protocols using RAG.
    
    Args:
        query: The search query about disaster protocols
        top_k: Number of relevant chunks to retrieve
        
    Returns:
        Formatted string with relevant protocol sections
    """
    rag = get_rag_instance()
    results = rag.search(query, top_k)
    
    if not results:
        return "No relevant protocols found."
    
    formatted_results = "### Relevant Disaster Protocols:\n\n"
    for i, result in enumerate(results, 1):
        formatted_results += f"**Result {i}** (from {result['source']}):\n"
        formatted_results += f"{result['text']}\n\n"
        formatted_results += f"_Relevance: {result['similarity_score']:.2%}_\n\n"
        formatted_results += "---\n\n"
    
    return formatted_results


def rebuild_rag_index() -> str:
    """Rebuild the RAG index from scratch. Use when documents are updated."""
    rag = get_rag_instance()
    rag.build_index()
    return "RAG index rebuilt successfully."
