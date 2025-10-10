from fastapi import APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List
import logging
from app.models.code_assistant import CodeAssistantStatus
from app.services.rag_pipeline import RAGPipeline

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
from app.services.vectorstore_service import VectorStoreService
vectorstore_service = VectorStoreService()
rag_pipeline = RAGPipeline()

@router.get("/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {"message": "Admin router is working!", "timestamp": "2025-01-01"}

@router.get("/chroma/status")
async def get_chroma_status() -> Dict[str, Any]:
    """Get ChromaDB status and collection info"""
    try:
        stats = await vectorstore_service.get_collection_stats()
        return {
            "status": "connected",
            "collection_name": stats.get('collection_name'),
            "total_documents": stats.get('total_chunks', 0),
            "file_types": stats.get('file_types', {}),
            "health": vectorstore_service.health_check()
        }
    except Exception as e:
        logger.error(f"Error getting ChromaDB status: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "health": False
        }

@router.get("/chroma/documents")
async def get_all_documents(limit: int = 50) -> Dict[str, Any]:
    """Get all documents from ChromaDB"""
    try:
        # Simple test first
        if not hasattr(vectorstore_service, 'collection') or not vectorstore_service.collection:
            return {
                "total_documents": 0,
                "documents": [],
                "limit": limit,
                "error": "ChromaDB collection not initialized"
            }
        
        # Get documents from collection
        try:
            # First try to get just IDs to test
            results = vectorstore_service.collection.get(
                limit=limit
            )
            
            if not results or not results.get('ids'):
                return {
                    "total_documents": 0,
                    "documents": [],
                    "limit": limit,
                    "message": "No documents found in collection"
                }
            
            documents = []
            ids = results.get('ids', [])
            docs = results.get('documents', [])
            metas = results.get('metadatas', [])
            
            for i, doc_id in enumerate(ids):
                documents.append({
                    'id': doc_id,
                    'content': docs[i] if i < len(docs) else '',
                    'metadata': metas[i] if i < len(metas) else {}
                })
            
            return {
                "total_documents": len(documents),
                "documents": documents,
                "limit": limit
            }
            
        except Exception as e:
            logger.error(f"ChromaDB get() error: {str(e)}")
            return {
                "total_documents": 0,
                "documents": [],
                "limit": limit,
                "error": f"ChromaDB error: {str(e)}"
            }
        
    except Exception as e:
        logger.error(f"General error in get_all_documents: {str(e)}")
        return {
            "total_documents": 0,
            "documents": [],
            "limit": limit,
            "error": f"General error: {str(e)}"
        }

@router.get("/chroma/search")
async def search_documents(query: str, limit: int = 10) -> Dict[str, Any]:
    """Search documents in ChromaDB"""
    try:
        # Use vectorstore service directly for search
        embedding = await rag_pipeline.embedding_service.embed_text(query)
        results = await vectorstore_service.query_similar(
            query_embedding=embedding,
            n_results=limit
        )
        
        return {
            "query": query,
            "results_count": len(results.get('documents', [])),
            "documents": results.get('documents', []),
            "metadatas": results.get('metadatas', []),
            "distances": results.get('distances', [])
        }
        
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/chroma/clear")
async def clear_chroma_db() -> Dict[str, Any]:
    """Clear all documents from ChromaDB"""
    try:
        result = await rag_pipeline.clear_knowledge_base()
        return result
    except Exception as e:
        logger.error(f"Error clearing ChromaDB: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chroma/collections")
async def list_collections() -> Dict[str, Any]:
    """List all collections in ChromaDB"""
    try:
        if not vectorstore_service.client:
            raise HTTPException(status_code=500, detail="ChromaDB client not initialized")
        
        collections = vectorstore_service.client.list_collections()
        
        collection_info = []
        for collection in collections:
            try:
                count = collection.count()
                collection_info.append({
                    "name": collection.name,
                    "id": collection.id,
                    "document_count": count,
                    "metadata": collection.metadata
                })
            except Exception as e:
                collection_info.append({
                    "name": collection.name,
                    "id": collection.id,
                    "document_count": "error",
                    "error": str(e)
                })
        
        return {
            "collections": collection_info,
            "total_collections": len(collection_info)
        }
        
    except Exception as e:
        logger.error(f"Error listing collections: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-data-files")
async def process_data_files() -> Dict[str, Any]:
    """Manually trigger processing of data directory files"""
    try:
        from app.services.rag_pipeline import RAGPipeline
        from pathlib import Path
        from app.config import settings
        
        rag_pipeline = RAGPipeline()
        
        data_dir = Path(settings.DATA_DIR)
        if not data_dir.exists():
            raise HTTPException(status_code=404, detail=f"Data directory {data_dir} does not exist")
        
        logger.info(f"Processing files from {data_dir}")
        
        # Supported file extensions
        supported_extensions = ['.md', '.py', '.js', '.ts', '.json', '.yaml', '.yml', '.txt', '.csv']
        
        files_processed = 0
        total_chunks = 0
        errors = []
        
        for file_path in data_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                try:
                    logger.info(f"Processing file: {file_path}")
                    
                    # Read file content
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Create metadata
                    metadata = {
                        'file_name': file_path.name,
                        'file_path': str(file_path),
                        'file_type': file_path.suffix,  # Keep the dot for chunking service
                        'file_size': len(content),
                        'source': 'manual_processing'
                    }
                    
                    # Process through RAG pipeline
                    result = await rag_pipeline.add_document(
                        doc_id=str(file_path),
                        content=content,
                        metadata=metadata
                    )
                    
                    if result['status'] == 'success':
                        files_processed += 1
                        total_chunks += result['chunks_added']
                    else:
                        errors.append(f"{file_path}: {result['message']}")
                    
                except Exception as e:
                    error_msg = f"Error processing file {file_path}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
        
        return {
            "status": "completed",
            "files_processed": files_processed,
            "total_chunks_added": total_chunks,
            "errors": errors,
            "message": f"Processed {files_processed} files, added {total_chunks} chunks"
        }
        
    except Exception as e:
        logger.error(f"Error in manual file processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
