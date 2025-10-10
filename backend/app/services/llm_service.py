import asyncio
from typing import AsyncGenerator, List, Dict
import logging
from groq import Groq

from app.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    """
    Service for interacting with Groq LLM API
    Handles both streaming and non-streaming responses
    """
    
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_CHAT_MODEL
        
    async def stream_chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat completion tokens from Groq API
        """
        try:
            # Convert messages to Groq format
            groq_messages = []
            for msg in messages:
                groq_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Create streaming completion
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=groq_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            # Yield tokens as they arrive
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Error in streaming chat completion: {str(e)}")
            yield f"Error: {str(e)}"
    
    async def get_chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """
        Get complete chat response (non-streaming)
        """
        try:
            # Convert messages to Groq format
            groq_messages = []
            for msg in messages:
                groq_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Create completion
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=groq_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error in chat completion: {str(e)}")
            return f"Error: {str(e)}"
    
    def format_messages_for_general_chat(self, user_message: str, conversation_history: List[Dict] = None) -> List[Dict[str, str]]:
        """
        Format messages for general chat mode
        """
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant. Engage in natural conversation, answer questions accurately, and provide thoughtful responses. Be concise but thorough."}
        ]
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-10:]:  # Last 10 messages
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return messages
