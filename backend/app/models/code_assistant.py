from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime

class CodeAssistantRequest(BaseModel):
    message: str
    session_id: str
    conversation_history: Optional[List[Dict[str, str]]] = []


class CodeAssistantStatus(BaseModel):
    documents_count: int
    chunks_count: int
    last_updated: Optional[str] = None
    is_ready: bool

class DocumentChunk(BaseModel):
    content: str
    metadata: Dict[str, Any]
    chunk_id: str
    
class RetrievalResult(BaseModel):
    chunks: List[DocumentChunk]
    query: str
    similarity_scores: List[float]
