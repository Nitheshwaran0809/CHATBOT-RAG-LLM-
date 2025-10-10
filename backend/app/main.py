from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.config import settings
from app.routers import chat, code_assistant, sessions

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(code_assistant.router, prefix="/api/code-assistant", tags=["Code Assistant"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["Sessions"])

# Admin router for ChromaDB management
from app.routers import admin
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])

async def process_data_directory(rag_pipeline):
    """Process all files in the data directory"""
    import os
    from pathlib import Path
    
    data_dir = Path(settings.DATA_DIR)
    if not data_dir.exists():
        logger.warning(f"Data directory {data_dir} does not exist")
        return
    
    logger.info(f"Processing files from {data_dir}")
    
    # Supported file extensions
    supported_extensions = ['.md', '.py', '.js', '.ts', '.json', '.yaml', '.yml', '.txt', '.csv']
    
    files_processed = 0
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
                    'source': 'data_directory'
                }
                
                # Process through RAG pipeline
                await rag_pipeline.add_document(
                    doc_id=str(file_path),
                    content=content,
                    metadata=metadata
                )
                
                files_processed += 1
                
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {str(e)}")
    
    logger.info(f"Processed {files_processed} files from data directory")

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    try:
        # Initialize and test services
        from app.services.embedding_service import EmbeddingService
        from app.services.vectorstore_service import VectorStoreService
        from app.services.rag_pipeline import RAGPipeline
        
        # Test embedding service
        embedding_service = EmbeddingService()
        logger.info(f"Embedding service initialized (provider: {embedding_service.embedding_provider})")
        
        # Test vector store
        vectorstore_service = VectorStoreService()
        if vectorstore_service.health_check():
            logger.info("ChromaDB connection successful")
        else:
            logger.warning("ChromaDB connection failed")
        
        # Test RAG pipeline and process data files
        rag_pipeline = RAGPipeline()
        
        # Process files from data directory on startup
        await process_data_directory(rag_pipeline)
        
        status = await rag_pipeline.get_pipeline_status()
        logger.info(f"RAG pipeline initialized - {status['total_chunks']} chunks available")
        
    except Exception as e:
        logger.error(f"Service initialization error: {str(e)}")
        # Don't fail startup, just log the error

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down application")
    # Close connections
    # Cleanup resources

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        from app.services.vectorstore_service import VectorStoreService
        from app.services.rag_pipeline import RAGPipeline
        
        # Check ChromaDB
        vectorstore_service = VectorStoreService()
        chroma_healthy = vectorstore_service.health_check()
        
        # Check RAG pipeline
        rag_pipeline = RAGPipeline()
        rag_status = await rag_pipeline.get_pipeline_status()
        
        return {
            "status": "healthy" if chroma_healthy else "degraded",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "groq_api": "configured",
            "chroma_db": "connected" if chroma_healthy else "disconnected",
            "rag_pipeline": {
                "ready": rag_status.get('is_ready', False),
                "chunks": rag_status.get('total_chunks', 0),
                "embedding_provider": rag_status.get('embedding_provider', 'unknown')
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "error": str(e)
        }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ChatGPT Clone with RAG Code Assistant API",
        "docs": "/docs",
        "health": "/health"
    }
