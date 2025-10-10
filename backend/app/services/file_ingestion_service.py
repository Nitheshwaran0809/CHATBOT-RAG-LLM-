import os
import tempfile
import shutil
from typing import List, Dict, Any, Tuple
import logging
from pathlib import Path
import asyncio
from datetime import datetime

from app.services.document_processor import DocumentProcessor
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.vectorstore_service import VectorStoreService
from app.core.constants import ALL_SUPPORTED_EXTENSIONS

logger = logging.getLogger(__name__)

class FileIngestionService:
    """
    Service for handling file uploads and processing them through the RAG pipeline
    """
    
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.chunking_service = ChunkingService()
        self.embedding_service = EmbeddingService()
        self.vectorstore_service = VectorStoreService()
        
        # Processing statistics
        self.processing_stats = {
            'files_processed': 0,
            'files_failed': 0,
            'chunks_created': 0,
            'total_size_bytes': 0,
            'processing_time_seconds': 0,
            'failed_files': []
        }
    
    async def process_uploaded_files(
        self, 
        uploaded_files: List[Dict[str, Any]],
        progress_callback=None
    ) -> Dict[str, Any]:
        """
        Process multiple uploaded files through the complete RAG pipeline
        
        Args:
            uploaded_files: List of file dictionaries with 'name', 'content', 'size'
            progress_callback: Optional callback for progress updates
            
        Returns:
            Processing results and statistics
        """
        start_time = datetime.utcnow()
        
        # Reset statistics
        self.processing_stats = {
            'files_processed': 0,
            'files_failed': 0,
            'chunks_created': 0,
            'total_size_bytes': 0,
            'processing_time_seconds': 0,
            'failed_files': []
        }
        
        logger.info(f"Starting processing of {len(uploaded_files)} files")
        
        try:
            # Validate files first
            valid_files, invalid_files = self._validate_files(uploaded_files)
            
            if invalid_files:
                logger.warning(f"Found {len(invalid_files)} invalid files")
                self.processing_stats['failed_files'].extend(invalid_files)
            
            if not valid_files:
                return self._build_result_summary(start_time, "No valid files to process")
            
            # Process files in batches to manage memory
            batch_size = 5
            all_chunks = []
            
            for i in range(0, len(valid_files), batch_size):
                batch = valid_files[i:i + batch_size]
                batch_num = i // batch_size + 1
                total_batches = (len(valid_files) + batch_size - 1) // batch_size
                
                logger.info(f"Processing batch {batch_num}/{total_batches}")
                
                if progress_callback:
                    progress_callback(f"Processing batch {batch_num}/{total_batches}", 
                                    (i / len(valid_files)) * 0.8)  # 80% for processing
                
                batch_chunks = await self._process_file_batch(batch)
                all_chunks.extend(batch_chunks)
            
            # Generate embeddings and store in vector database
            if all_chunks:
                if progress_callback:
                    progress_callback("Generating embeddings...", 0.8)
                
                await self._store_chunks_in_vectordb(all_chunks, progress_callback)
            
            # Calculate final statistics
            end_time = datetime.utcnow()
            self.processing_stats['processing_time_seconds'] = (end_time - start_time).total_seconds()
            
            logger.info(f"Processing completed: {self.processing_stats}")
            
            if progress_callback:
                progress_callback("Processing complete!", 1.0)
            
            return self._build_result_summary(start_time, "Success")
            
        except Exception as e:
            logger.error(f"Error in file processing: {str(e)}")
            return self._build_result_summary(start_time, f"Error: {str(e)}")
    
    def _validate_files(self, uploaded_files: List[Dict]) -> Tuple[List[Dict], List[str]]:
        """Validate uploaded files and return valid/invalid lists"""
        valid_files = []
        invalid_files = []
        
        for file_info in uploaded_files:
            filename = file_info.get('name', '')
            file_size = file_info.get('size', 0)
            
            # Check file extension
            file_ext = Path(filename).suffix.lower()
            if not file_ext and filename.lower() not in ['dockerfile', 'makefile', 'readme']:
                invalid_files.append(f"{filename}: No file extension")
                continue
            
            if file_ext and file_ext not in ALL_SUPPORTED_EXTENSIONS:
                invalid_files.append(f"{filename}: Unsupported file type ({file_ext})")
                continue
            
            # Check file size (50MB limit)
            max_size = 50 * 1024 * 1024  # 50MB
            if file_size > max_size:
                invalid_files.append(f"{filename}: File too large ({file_size / 1024 / 1024:.1f}MB)")
                continue
            
            # Check if content exists
            if not file_info.get('content'):
                invalid_files.append(f"{filename}: Empty file")
                continue
            
            valid_files.append(file_info)
            self.processing_stats['total_size_bytes'] += file_size
        
        return valid_files, invalid_files
    
    async def _process_file_batch(self, file_batch: List[Dict]) -> List[Dict]:
        """Process a batch of files and return chunks"""
        batch_chunks = []
        
        for file_info in file_batch:
            try:
                filename = file_info['name']
                content = file_info['content']
                
                logger.info(f"Processing file: {filename}")
                
                # Create temporary file for processing
                with tempfile.NamedTemporaryFile(mode='w', suffix=Path(filename).suffix, 
                                               delete=False, encoding='utf-8') as temp_file:
                    temp_file.write(content)
                    temp_file_path = temp_file.name
                
                try:
                    # Process through document processor
                    processed_content, metadata = await self.document_processor.process_file(
                        temp_file_path, filename
                    )
                    
                    # Add upload metadata
                    metadata.update({
                        'upload_timestamp': datetime.utcnow().isoformat(),
                        'file_size': len(content),
                        'source': 'upload'
                    })
                    
                    # Chunk the content
                    chunks = await self.chunking_service.chunk_document(processed_content, metadata)
                    
                    batch_chunks.extend(chunks)
                    self.processing_stats['files_processed'] += 1
                    self.processing_stats['chunks_created'] += len(chunks)
                    
                    logger.info(f"Successfully processed {filename}: {len(chunks)} chunks")
                    
                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
                
            except Exception as e:
                error_msg = f"{filename}: {str(e)}"
                logger.error(f"Error processing file: {error_msg}")
                self.processing_stats['failed_files'].append(error_msg)
                self.processing_stats['files_failed'] += 1
        
        return batch_chunks
    
    async def _store_chunks_in_vectordb(self, chunks: List[Dict], progress_callback=None):
        """Store chunks in vector database with embeddings"""
        
        # Process in smaller batches for embedding generation
        embedding_batch_size = 10
        
        for i in range(0, len(chunks), embedding_batch_size):
            batch = chunks[i:i + embedding_batch_size]
            
            if progress_callback:
                progress = 0.8 + (i / len(chunks)) * 0.2  # 80-100% range
                progress_callback(f"Generating embeddings ({i+1}/{len(chunks)})", progress)
            
            # Extract content and metadata
            documents = [chunk['content'] for chunk in batch]
            metadatas = [chunk['metadata'] for chunk in batch]
            
            # Generate embeddings
            embeddings = await self.embedding_service.embed_texts(documents)
            
            # Store in vector database
            await self.vectorstore_service.add_documents(
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings
            )
            
            logger.info(f"Stored batch {i//embedding_batch_size + 1} in vector database")
    
    def _build_result_summary(self, start_time: datetime, status: str) -> Dict[str, Any]:
        """Build processing result summary"""
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        return {
            'status': status,
            'files_processed': self.processing_stats['files_processed'],
            'files_failed': self.processing_stats['files_failed'],
            'chunks_created': self.processing_stats['chunks_created'],
            'total_size_mb': round(self.processing_stats['total_size_bytes'] / 1024 / 1024, 2),
            'processing_time_seconds': round(processing_time, 2),
            'failed_files': self.processing_stats['failed_files'],
            'timestamp': end_time.isoformat()
        }
    
    async def get_ingestion_stats(self) -> Dict[str, Any]:
        """Get current ingestion statistics"""
        vectorstore_stats = await self.vectorstore_service.get_collection_stats()
        
        return {
            'total_chunks': vectorstore_stats.get('total_chunks', 0),
            'file_types': vectorstore_stats.get('file_types', {}),
            'last_processing_stats': self.processing_stats,
            'supported_extensions': ALL_SUPPORTED_EXTENSIONS,
            'max_file_size_mb': 50
        }
    
    async def clear_all_data(self) -> Dict[str, Any]:
        """Clear all ingested data"""
        try:
            deleted_count = await self.vectorstore_service.clear_collection()
            
            # Reset processing stats
            self.processing_stats = {
                'files_processed': 0,
                'files_failed': 0,
                'chunks_created': 0,
                'total_size_bytes': 0,
                'processing_time_seconds': 0,
                'failed_files': []
            }
            
            return {
                'status': 'success',
                'chunks_deleted': deleted_count,
                'message': f'Cleared {deleted_count} chunks from knowledge base'
            }
            
        except Exception as e:
            logger.error(f"Error clearing data: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error clearing data: {str(e)}'
            }
