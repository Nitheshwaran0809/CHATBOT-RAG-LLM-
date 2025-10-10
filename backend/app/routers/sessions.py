from fastapi import APIRouter, HTTPException
from typing import List, Dict
from app.models.session import ConversationHistory, SessionClearResponse
from app.services.session_service import SessionService

router = APIRouter()

# Initialize session service
session_service = SessionService()

@router.get("/{session_id}/history")
async def get_session_history(session_id: str) -> ConversationHistory:
    """
    Get conversation history for a session
    """
    try:
        messages = session_service.get_conversation_history(session_id)
        
        return ConversationHistory(
            session_id=session_id,
            messages=messages,
            message_count=len(messages)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/clear")
async def clear_session_history(session_id: str) -> SessionClearResponse:
    """
    Clear conversation history for a session
    """
    try:
        messages_cleared = session_service.clear_conversation_history(session_id)
        
        return SessionClearResponse(
            status="cleared",
            messages_cleared=messages_cleared
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
