import asyncio
from typing import List, Union
import logging
import hashlib
import json
from groq import Groq

from app.config import settings

# Try to import sentence_transformers, but don't fail if not available
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None
    np = None

logger = logging.getLogger(__name__)

class EmbeddingService:
    """
    Service for generating embeddings using Groq API (primary) 
    with sentence-transformers as fallback
    """
    
    def __init__(self):
        self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
        self.local_model = None
        self.embedding_provider = settings.EMBEDDING_PROVIDER
        
        # Initialize local model if needed
        if self.embedding_provider == "local":
            self._init_local_model()
    
    def _init_local_model(self):
        """Initialize local sentence transformer model"""
        try:
            if not SENTENCE_TRANSFORMERS_AVAILABLE:
                logger.warning("sentence-transformers not available, using simple hash-based embeddings")
                self.local_model = None
                return
                
            logger.info(f"Loading local embedding model: {settings.LOCAL_EMBEDDING_MODEL}")
            self.local_model = SentenceTransformer(settings.LOCAL_EMBEDDING_MODEL)
            logger.info("Local embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load local embedding model: {str(e)}")
            self.local_model = None
    
    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        """
        try:
            if self.embedding_provider == "groq":
                return await self._embed_with_groq(text)
            else:
                return await self._embed_with_local(text)
        except Exception as e:
            logger.error(f"Primary embedding failed, trying fallback: {str(e)}")
            # Try fallback method
            if self.embedding_provider == "groq":
                return await self._embed_with_local(text)
            else:
                return await self._embed_with_groq(text)
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        """
        embeddings = []
        for text in texts:
            embedding = await self.embed_text(text)
            embeddings.append(embedding)
        return embeddings
    
    async def _embed_with_groq(self, text: str) -> List[float]:
        """
        Generate embedding using Groq API
        Note: Groq may not have embedding endpoints yet, this is a placeholder
        """
        try:
            # TODO: Replace with actual Groq embedding API when available
            # For now, use local model as fallback
            logger.warning("Groq embeddings not yet implemented, falling back to local model")
            return await self._embed_with_local(text)
            
            # Future Groq embedding implementation:
            # response = self.groq_client.embeddings.create(
            #     model=settings.GROQ_EMBEDDING_MODEL,
            #     input=text
            # )
            # return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Groq embedding failed: {str(e)}")
            raise
    
    async def _embed_with_local(self, text: str) -> List[float]:
        """
        Generate embedding using local sentence transformer or simple hash fallback
        """
        try:
            if self.local_model is None and SENTENCE_TRANSFORMERS_AVAILABLE:
                self._init_local_model()
            
            if self.local_model is not None:
                # Use sentence transformers if available
                loop = asyncio.get_event_loop()
                embedding = await loop.run_in_executor(
                    None, 
                    self.local_model.encode, 
                    text
                )
                
                # Convert numpy array to list
                if isinstance(embedding, np.ndarray):
                    embedding = embedding.tolist()
                
                return embedding
            else:
                # Fallback to simple hash-based embedding
                logger.info("Using simple hash-based embedding fallback")
                return self._simple_hash_embedding(text)
            
        except Exception as e:
            logger.error(f"Local embedding failed, using hash fallback: {str(e)}")
            return self._simple_hash_embedding(text)
    
    def _simple_hash_embedding(self, text: str, dimension: int = 384) -> List[float]:
        """
        Generate a simple hash-based embedding as fallback
        """
        # Create multiple hash values to fill the dimension
        embeddings = []
        for i in range(0, dimension, 32):  # 32 floats per hash (assuming 4 bytes per float)
            hash_input = f"{text}_{i}"
            hash_obj = hashlib.sha256(hash_input.encode())
            hash_bytes = hash_obj.digest()
            
            # Convert bytes to floats
            for j in range(0, min(32, dimension - i)):
                if j * 4 + 3 < len(hash_bytes):
                    # Convert 4 bytes to float, normalize to [-1, 1]
                    byte_val = int.from_bytes(hash_bytes[j*4:(j+1)*4], 'big')
                    float_val = (byte_val / (2**32 - 1)) * 2 - 1
                    embeddings.append(float_val)
                else:
                    embeddings.append(0.0)
        
        return embeddings[:dimension]
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by current model
        """
        if self.embedding_provider == "groq":
            # TODO: Return actual Groq embedding dimension
            return 384  # Placeholder, typically 1536 for OpenAI-style models
        else:
            if self.local_model is None and SENTENCE_TRANSFORMERS_AVAILABLE:
                self._init_local_model()
            if self.local_model is not None:
                return self.local_model.get_sentence_embedding_dimension()
            return 384  # Default dimension for hash-based embeddings
