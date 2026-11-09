"""
STEP 7: Upload embeddings to FAISS vector database
"""

import json
import os
from typing import List, Dict
from pathlib import Path
import logging
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FaissUploader:
    """Upload embeddings to local FAISS index"""
    
    def __init__(self, collection_name: str = "cosmetic_ingredients"):
        self.logger = logger
        self.collection_name = collection_name
        self.index_path = os.getenv("FAISS_INDEX_PATH", "./data/faiss_index")
        self.embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        self.logger.info(f"Initialized FAISS Uploader. Index path: {self.index_path}")
        
    def create_collection(self, vector_size: int = 384):
        """No-op for FAISS, index is created during upload"""
        self.logger.info("FAISS index will be created during upload")
            
    def upload_embeddings(self, ingredients_with_embeddings: List[Dict]):
        """
        Upload ingredient embeddings to FAISS
        
        Args:
            ingredients_with_embeddings: List of ingredients with embeddings
        """
        self.logger.info(f"Uploading {len(ingredients_with_embeddings)} ingredients to FAISS...")
        
        documents = []
        
        for ingredient in ingredients_with_embeddings:
            metadata = {
                'name': ingredient['name'],
                'purpose': ingredient['purpose'],
                'description': ingredient['description'],
                'safety_score': ingredient.get('safety_score'),
                'concerns': ingredient['concerns'],
                'sources': ingredient.get('sources', [])
            }
            # FAISS uses Document objects
            text = ingredient.get('embedding_text', ingredient['name'])
            doc = Document(page_content=text, metadata=metadata)
            documents.append(doc)
            
        # Create FAISS index from documents
        self.logger.info("Building FAISS index...")
        vectorstore = FAISS.from_documents(documents, self.embeddings_model)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        
        # Save to disk
        vectorstore.save_local(self.index_path)
        self.logger.info(f"Upload complete! Saved to {self.index_path}")
        
    def test_search(self, query: str, top_k: int = 3):
        """
        Test vector search
        
        Args:
            query: Search query
            top_k: Number of results to return
        """
        self.logger.info(f"Testing search for: {query}")
        
        if not os.path.exists(self.index_path):
            self.logger.error(f"FAISS index not found at {self.index_path}")
            return
            
        vectorstore = FAISS.load_local(self.index_path, self.embeddings_model, allow_dangerous_deserialization=True)
        
        results = vectorstore.similarity_search_with_score(query, k=top_k)
        
        self.logger.info(f"Found {len(results)} results:")
        for i, (doc, score) in enumerate(results, 1):
            # FAISS L2 distance (lower is better), we might want to convert to similarity score
            self.logger.info(f"{i}. {doc.metadata.get('name', 'Unknown')} (L2 distance: {score:.3f})")
            self.logger.info(f"   Purpose: {doc.metadata.get('purpose', '')}")
