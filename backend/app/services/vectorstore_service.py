import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import logging
import uuid
from datetime import datetime

from app.config import settings

logger = logging.getLogger(__name__)

class VectorStoreService:
    """
    Service for managing ChromaDB vector store operations
    """
    
    def __init__(self):
        self.client = None
        self.collection = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Initialize ChromaDB client with persistent storage
            self.client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIR
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION_NAME,
                metadata={"description": "Code Assistant RAG collection"}
            )
            
            logger.info(f"ChromaDB initialized with collection: {settings.CHROMA_COLLECTION_NAME}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {str(e)}")
            raise
    
    async def add_documents(
        self, 
        documents: List[str], 
        metadatas: List[Dict[str, Any]], 
        embeddings: List[List[float]]
    ) -> List[str]:
        """
        Add documents to the vector store
        Returns list of document IDs
        """
        try:
            # Generate unique IDs for documents
            ids = [str(uuid.uuid4()) for _ in documents]
            
            # Add timestamp to metadata
            for metadata in metadatas:
                metadata['added_at'] = datetime.utcnow().isoformat()
            
            # Add to collection
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings,
                ids=ids
            )
            
            logger.info(f"Added {len(documents)} documents to vector store")
            return ids
            
        except Exception as e:
            logger.error(f"Failed to add documents: {str(e)}")
            raise
    
    async def add_document(
        self, 
        doc_id: str,
        content: str, 
        embedding: List[float],
        metadata: Dict[str, Any]
    ) -> str:
        """
        Add a single document to the vector store
        Returns document ID
        """
        try:
            # Add timestamp to metadata
            metadata['added_at'] = datetime.utcnow().isoformat()
            
            # Add to collection
            self.collection.add(
                ids=[doc_id],
                documents=[content],
                embeddings=[embedding],
                metadatas=[metadata]
            )
            
            logger.info(f"Added document {doc_id} to vector store")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to add document {doc_id}: {str(e)}")
            raise
    
    async def query_similar(
        self, 
        query_embedding: List[float], 
        n_results: int = 8,
        where_filter: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Query for similar documents
        """
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_filter,
                include=['documents', 'metadatas', 'distances']
            )
            
            return {
                'documents': results['documents'][0] if results['documents'] else [],
                'metadatas': results['metadatas'][0] if results['metadatas'] else [],
                'distances': results['distances'][0] if results['distances'] else [],
                'ids': results['ids'][0] if results['ids'] else []
            }
            
        except Exception as e:
            logger.error(f"Failed to query vector store: {str(e)}")
            return {
                'documents': [],
                'metadatas': [],
                'distances': [],
                'ids': []
            }
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection
        """
        try:
            count = self.collection.count()
            
            # Get sample of metadata to understand document types
            sample_results = self.collection.get(limit=10, include=['metadatas'])
            
            file_types = {}
            for metadata in sample_results.get('metadatas', []):
                file_type = metadata.get('file_type', 'unknown')
                file_types[file_type] = file_types.get(file_type, 0) + 1
            
            return {
                'total_chunks': count,
                'file_types': file_types,
                'collection_name': settings.CHROMA_COLLECTION_NAME
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {str(e)}")
            return {
                'total_chunks': 0,
                'file_types': {},
                'collection_name': settings.CHROMA_COLLECTION_NAME
            }
    
    async def clear_collection(self) -> int:
        """
        Clear all documents from the collection
        Returns number of documents deleted
        """
        try:
            # Get current count
            count = self.collection.count()
            
            # Delete the collection and recreate it
            self.client.delete_collection(settings.CHROMA_COLLECTION_NAME)
            
            # Recreate collection
            self.collection = self.client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION_NAME,
                metadata={"description": "Code Assistant RAG collection"}
            )
            
            logger.info(f"Cleared {count} documents from vector store")
            return count
            
        except Exception as e:
            logger.error(f"Failed to clear collection: {str(e)}")
            return 0
    
    async def delete_documents_by_filter(self, where_filter: Dict) -> int:
        """
        Delete documents matching a filter
        """
        try:
            # First, get the IDs of documents to delete
            results = self.collection.get(
                where=where_filter,
                include=['ids']
            )
            
            ids_to_delete = results.get('ids', [])
            
            if ids_to_delete:
                self.collection.delete(ids=ids_to_delete)
                logger.info(f"Deleted {len(ids_to_delete)} documents")
            
            return len(ids_to_delete)
            
        except Exception as e:
            logger.error(f"Failed to delete documents: {str(e)}")
            return 0
    
    def health_check(self) -> bool:
        """
        Check if vector store is healthy
        """
        try:
            # Try to get collection count
            self.collection.count()
            return True
        except Exception as e:
            logger.error(f"Vector store health check failed: {str(e)}")
            return False
