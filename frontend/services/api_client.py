import requests
from typing import List, Dict, Any, Generator
import streamlit as st
import json
import logging

logger = logging.getLogger(__name__)

class APIClient:
    """
    Client for communicating with FastAPI backend
    """
    
    def __init__(self, backend_url: str):
        self.backend_url = backend_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def chat_general(self, message: str, session_id: str) -> Generator[str, None, None]:
        """Send message to general chat endpoint and yield streaming tokens"""
        try:
            response = self.session.post(
                f"{self.backend_url}/api/chat/general",
                json={
                    "message": message,
                    "session_id": session_id,
                    "conversation_history": []
                },
                stream=True
            )
            response.raise_for_status()
            
            # Handle streaming response
            for line in response.iter_lines(decode_unicode=True):
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])  # Remove 'data: ' prefix
                        if data.get('token'):
                            yield data['token']
                        if data.get('complete'):
                            break
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            logger.error(f"Error in chat_general: {str(e)}")
            yield f"Error: {str(e)}"
    
    def chat_code_assistant(
        self, 
        message: str, 
        session_id: str,
        conversation_history: List[Dict] = None
    ) -> Generator[str, None, None]:
        """Send message to code assistant endpoint (RAG) and yield streaming tokens"""
        try:
            response = self.session.post(
                f"{self.backend_url}/api/chat/code-assistant",
                json={
                    "message": message,
                    "session_id": session_id,
                    "conversation_history": conversation_history or []
                },
                stream=True
            )
            response.raise_for_status()
            
            # Handle streaming response
            for line in response.iter_lines(decode_unicode=True):
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])  # Remove 'data: ' prefix
                        if data.get('token'):
                            yield data['token']
                        if data.get('complete'):
                            break
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            logger.error(f"Error in chat_code_assistant: {str(e)}")
            yield f"Error: {str(e)}"
    
    def get_code_assistant_status(self) -> Dict[str, Any]:
        """Get status of uploaded documents"""
        try:
            response = self.session.get(
                f"{self.backend_url}/api/code-assistant/status"
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting status: {str(e)}")
            return {
                "is_ready": False,
                "documents_count": 0,
                "chunks_count": 0,
                "error": str(e)
            }
    
    
    def clear_code_assistant(self) -> Dict[str, Any]:
        """Clear all uploaded documents (Phase 2)"""
        try:
            response = self.session.delete(
                f"{self.backend_url}/api/code-assistant/clear"
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def clear_session(self, session_id: str) -> Dict[str, Any]:
        """Clear conversation history"""
        try:
            response = self.session.post(
                f"{self.backend_url}/api/sessions/{session_id}/clear"
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error clearing session: {str(e)}")
            return {"error": str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """Check if backend is healthy"""
        try:
            response = self.session.get(f"{self.backend_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
