from typing import Dict, List, Optional
import uuid
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SessionService:
    """
    Service for managing user sessions and conversation history
    In-memory storage for simplicity (can be replaced with Redis/DB)
    """
    
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
        self.conversation_histories: Dict[str, List[Dict]] = {}
    
    def create_session(self, mode: str = "general") -> str:
        """
        Create a new session and return session ID
        """
        session_id = str(uuid.uuid4())
        
        self.sessions[session_id] = {
            "session_id": session_id,
            "created_at": datetime.utcnow(),
            "last_active": datetime.utcnow(),
            "mode": mode
        }
        
        self.conversation_histories[session_id] = []
        
        logger.info(f"Created new session: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        Get session information
        """
        return self.sessions.get(session_id)
    
    def update_session_activity(self, session_id: str):
        """
        Update last active timestamp for session
        """
        if session_id in self.sessions:
            self.sessions[session_id]["last_active"] = datetime.utcnow()
    
    def add_message_to_history(self, session_id: str, role: str, content: str):
        """
        Add a message to conversation history
        """
        if session_id not in self.conversation_histories:
            self.conversation_histories[session_id] = []
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.conversation_histories[session_id].append(message)
        self.update_session_activity(session_id)
        
        # Keep only last 50 messages to prevent memory bloat
        if len(self.conversation_histories[session_id]) > 50:
            self.conversation_histories[session_id] = self.conversation_histories[session_id][-50:]
    
    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """
        Get conversation history for a session
        """
        return self.conversation_histories.get(session_id, [])
    
    def clear_conversation_history(self, session_id: str) -> int:
        """
        Clear conversation history for a session
        Returns number of messages cleared
        """
        if session_id in self.conversation_histories:
            message_count = len(self.conversation_histories[session_id])
            self.conversation_histories[session_id] = []
            logger.info(f"Cleared {message_count} messages for session {session_id}")
            return message_count
        return 0
    
    def cleanup_expired_sessions(self, timeout_minutes: int = 60):
        """
        Remove expired sessions (older than timeout_minutes)
        """
        cutoff_time = datetime.utcnow() - timedelta(minutes=timeout_minutes)
        expired_sessions = []
        
        for session_id, session_data in self.sessions.items():
            if session_data["last_active"] < cutoff_time:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
            if session_id in self.conversation_histories:
                del self.conversation_histories[session_id]
            logger.info(f"Cleaned up expired session: {session_id}")
        
        return len(expired_sessions)
    
    def get_or_create_session(self, session_id: Optional[str] = None, mode: str = "general") -> str:
        """
        Get existing session or create new one if not found
        """
        if session_id and session_id in self.sessions:
            self.update_session_activity(session_id)
            return session_id
        else:
            return self.create_session(mode)
