from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class Session(BaseModel):
    session_id: str
    created_at: datetime
    last_active: datetime
    mode: str  # "general" or "code_assistant"

class ConversationHistory(BaseModel):
    session_id: str
    messages: List[Dict[str, str]]
    message_count: int
    
class SessionClearResponse(BaseModel):
    status: str
    messages_cleared: int
