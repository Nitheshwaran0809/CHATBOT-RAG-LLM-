from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    message: str
    session_id: str
    conversation_history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: datetime
    
class StreamingChatResponse(BaseModel):
    """For streaming responses"""
    token: str
    session_id: str
    is_complete: bool = False
