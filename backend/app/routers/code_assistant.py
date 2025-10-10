from fastapi import APIRouter, HTTPException
from typing import List
import logging
from app.models.code_assistant import CodeAssistantStatus
from app.services.rag_pipeline import RAGPipeline

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
rag_pipeline = RAGPipeline()

@router.get("/status")
async def get_code_assistant_status() -> CodeAssistantStatus:
    """
    Get status of uploaded documents and vector store
    """
    try:
        status = await rag_pipeline.get_pipeline_status()
        
        return CodeAssistantStatus(
            documents_count=len(status.get('file_types', {})),
            chunks_count=status.get('total_chunks', 0),
            last_updated=None,  # Will be implemented when we add upload functionality
            is_ready=status.get('is_ready', False)
        )
    except Exception as e:
        return CodeAssistantStatus(
            documents_count=0,
            chunks_count=0,
            last_updated=None,
            is_ready=False
        )


@router.delete("/clear")
async def clear_documents():
    """
    Clear all uploaded documents from vector store
    """
    try:
        result = await rag_pipeline.clear_knowledge_base()
        
        if result.get('status') == 'success':
            return {
                "status": "cleared",
                "chunks_deleted": result.get('deleted_chunks', 0),
                "message": result.get('message', 'Knowledge base cleared')
            }
        else:
            raise HTTPException(status_code=500, detail=result.get('message', 'Failed to clear'))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
