from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import logging
import json

from app.models.chat import ChatRequest, ChatResponse
from app.services.llm_service import LLMService
from app.services.session_service import SessionService
from app.services.rag_pipeline import RAGPipeline

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
llm_service = LLMService()
session_service = SessionService()
rag_pipeline = RAGPipeline()

async def should_use_rag(message: str) -> bool:
    """
    Determine if a message should use RAG or just general LLM
    """
    message_lower = message.lower().strip()
    
    # Simple greetings and casual conversation - use general LLM
    simple_patterns = [
        'hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening',
        'how are you', 'what\'s up', 'thanks', 'thank you', 'bye', 'goodbye',
        'ok', 'okay', 'yes', 'no', 'sure', 'great', 'awesome', 'cool'
    ]
    
    # Check if it's a simple greeting/response
    if any(pattern in message_lower for pattern in simple_patterns) and len(message.split()) <= 3:
        return False
    
    # Project-related keywords - use RAG
    project_keywords = [
        'project', 'code', 'api', 'endpoint', 'backend', 'frontend', 'docker',
        'fastapi', 'streamlit', 'chromadb', 'groq', 'rag', 'database',
        'deployment', 'container', 'service', 'function', 'class', 'method',
        'error', 'bug', 'fix', 'implement', 'create', 'add', 'modify', 'update',
        'architecture', 'structure', 'design', 'pattern', 'configuration',
        'troubleshoot', 'debug', 'optimize', 'performance'
    ]
    
    # Check if message contains project-related keywords
    if any(keyword in message_lower for keyword in project_keywords):
        return True
    
    # Questions about "this", "my", "our" likely refer to the project
    if any(word in message_lower for word in ['this project', 'my project', 'our project', 'this code', 'my code']):
        return True
    
    # Default to general LLM for other cases
    return False

@router.post("/general")
async def chat_general(request: ChatRequest):
    """
    General chat endpoint without RAG
    Streams response from Groq LLM
    """
    try:
        # Get or create session
        session_id = session_service.get_or_create_session(request.session_id, "general")
        
        # Get conversation history
        conversation_history = session_service.get_conversation_history(session_id)
        
        # Add user message to history
        session_service.add_message_to_history(session_id, "user", request.message)
        
        # Format messages for LLM
        messages = llm_service.format_messages_for_general_chat(
            user_message=request.message,
            conversation_history=conversation_history
        )
        
        # Stream response
        async def generate_response() -> AsyncGenerator[str, None]:
            full_response = ""
            async for token in llm_service.stream_chat_completion(messages):
                full_response += token
                # Send token as JSON for easier parsing on frontend
                yield f"data: {json.dumps({'token': token, 'session_id': session_id})}\n\n"
            
            # Add assistant response to history
            session_service.add_message_to_history(session_id, "assistant", full_response)
            
            # Send completion signal
            yield f"data: {json.dumps({'token': '', 'session_id': session_id, 'complete': True})}\n\n"
        
        return StreamingResponse(
            generate_response(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*"
            }
        )
        
    except Exception as e:
        logger.error(f"Error in general chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/code-assistant")
async def chat_code_assistant(request: ChatRequest):
    """
    Code assistant chat endpoint with RAG
    Uses RAG pipeline to provide context-aware responses
    """
    try:
        # Get or create session
        session_id = session_service.get_or_create_session(request.session_id, "code_assistant")
        
        # Get conversation history
        conversation_history = session_service.get_conversation_history(session_id)
        
        # Add user message to history
        session_service.add_message_to_history(session_id, "user", request.message)
        
        # Smart routing: Check if query needs RAG or just general LLM
        needs_rag = await should_use_rag(request.message)
        pipeline_status = await rag_pipeline.get_pipeline_status()
        
        if needs_rag and not pipeline_status.get('is_ready'):
            # Project question but no documents available
            async def generate_response() -> AsyncGenerator[str, None]:
                response = "I don't have access to your project documentation yet. Please add your project files to the `backend/data/` directory and restart the backend to enable project-specific assistance."
                yield f"data: {json.dumps({'token': response, 'session_id': session_id, 'complete': True})}\n\n"
        elif needs_rag and pipeline_status.get('is_ready'):
            # Use RAG pipeline for project questions
            async def generate_response() -> AsyncGenerator[str, None]:
                full_response = ""
                async for token in rag_pipeline.process_query(
                    query=request.message,
                    session_id=session_id,
                    conversation_history=conversation_history,
                    top_k=8
                ):
                    full_response += token
                    yield f"data: {json.dumps({'token': token, 'session_id': session_id})}\n\n"
                
                # Add assistant response to history
                session_service.add_message_to_history(session_id, "assistant", full_response)
                
                # Send completion signal
                yield f"data: {json.dumps({'token': '', 'session_id': session_id, 'complete': True})}\n\n"
        else:
            # Use general LLM for simple questions/greetings
            async def generate_response() -> AsyncGenerator[str, None]:
                # Simple conversation without RAG
                messages = [
                    {"role": "system", "content": "You are a helpful AI assistant. Be concise and friendly."},
                    {"role": "user", "content": request.message}
                ]
                
                # Add conversation history
                for msg in conversation_history[-5:]:  # Last 5 messages for context
                    messages.insert(-1, msg)
                
                full_response = ""
                async for token in llm_service.stream_chat_completion(messages):
                    full_response += token
                    yield f"data: {json.dumps({'token': token, 'session_id': session_id})}\n\n"
                
                # Add assistant response to history
                session_service.add_message_to_history(session_id, "assistant", full_response)
                
                # Send completion signal
                yield f"data: {json.dumps({'token': '', 'session_id': session_id, 'complete': True})}\n\n"
        
        return StreamingResponse(
            generate_response(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*"
            }
        )
        
    except Exception as e:
        logger.error(f"Error in code assistant chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
