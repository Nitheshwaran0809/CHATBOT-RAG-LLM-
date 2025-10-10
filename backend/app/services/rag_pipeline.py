from typing import List, Dict, AsyncGenerator
import logging

from app.services.llm_service import LLMService
from app.services.embedding_service import EmbeddingService
from app.services.vectorstore_service import VectorStoreService
from app.core.prompts import build_rag_prompt, CODE_ASSISTANT_SYSTEM_PROMPT
from app.core.code_prompts import (
    build_code_generation_prompt, 
    build_debugging_prompt, 
    build_architecture_prompt,
    build_code_review_prompt
)

logger = logging.getLogger(__name__)

class RAGPipeline:
    """
    Custom RAG pipeline without any framework.
    Simple, explicit, maintainable.
    """
    
    def __init__(self):
        self.llm_service = LLMService()
        self.embedding_service = EmbeddingService()
        self.vectorstore_service = VectorStoreService()
    
    async def process_query(
        self, 
        query: str, 
        session_id: str,
        conversation_history: List[Dict],
        top_k: int = 8
    ) -> AsyncGenerator[str, None]:
        """
        Enhanced RAG pipeline with intelligent prompt selection:
        1. Embed query
        2. Retrieve relevant chunks
        3. Analyze query type and build specialized prompt
        4. Stream LLM response
        """
        try:
            # Step 1: Embed the user query
            logger.info(f"Embedding query for session {session_id}")
            query_embedding = await self.embedding_service.embed_text(query)
            
            # Step 2: Retrieve top-k similar chunks from ChromaDB
            logger.info(f"Retrieving {top_k} similar chunks")
            results = await self.vectorstore_service.query_similar(
                query_embedding=query_embedding,
                n_results=top_k
            )
            
            # Step 3: Format retrieved context
            context = self._format_context(results)
            
            # Step 4: Determine query type and build appropriate prompt
            prompt = self._build_intelligent_prompt(query, context, conversation_history)
            
            # Step 5: Format messages for LLM
            messages = [{"role": "user", "content": prompt}]
            
            # Step 6: Stream response from LLM
            logger.info("Streaming LLM response with enhanced prompt")
            async for token in self.llm_service.stream_chat_completion(messages):
                yield token
                
        except Exception as e:
            logger.error(f"RAG pipeline error: {str(e)}")
            yield f"Error in RAG pipeline: {str(e)}"
    
    def _build_intelligent_prompt(
        self, 
        query: str, 
        context: str, 
        conversation_history: List[Dict]
    ) -> str:
        """
        Build intelligent prompt based on query type analysis
        """
        query_lower = query.lower()
        
        # Detect debugging/error queries
        if any(word in query_lower for word in [
            "error", "bug", "issue", "problem", "fix", "debug", 
            "exception", "traceback", "fails", "broken", "not working"
        ]):
            return build_debugging_prompt(context, query, conversation_history)
        
        # Detect architecture/design queries
        elif any(word in query_lower for word in [
            "architecture", "design", "pattern", "structure", "organize",
            "scalable", "performance", "optimize", "refactor", "improve"
        ]):
            return build_architecture_prompt(context, query, conversation_history)
        
        # Detect code review queries
        elif any(word in query_lower for word in [
            "review", "check", "validate", "best practice", "code quality",
            "security", "vulnerability", "clean up"
        ]):
            return build_code_review_prompt(context, query, conversation_history)
        
        # Default to enhanced code generation prompt
        else:
            return build_code_generation_prompt(context, query, conversation_history)
    
    def _format_context(self, results: Dict) -> str:
        """Format retrieved chunks into readable context"""
        if not results['documents']:
            return "No relevant code context found in your project."
        
        context_parts = []
        
        for doc, metadata, distance in zip(
            results['documents'], 
            results['metadatas'], 
            results['distances']
        ):
            # Format each chunk with metadata
            filename = metadata.get('filename', 'Unknown file')
            file_type = metadata.get('file_type', 'unknown')
            start_line = metadata.get('start_line', 'N/A')
            end_line = metadata.get('end_line', 'N/A')
            function_name = metadata.get('function_name', '')
            class_name = metadata.get('class_name', '')
            
            # Build context header
            header_parts = [f"File: {filename}"]
            
            if start_line != 'N/A' and end_line != 'N/A':
                header_parts.append(f"Lines: {start_line}-{end_line}")
            
            if class_name:
                header_parts.append(f"Class: {class_name}")
            
            if function_name:
                header_parts.append(f"Function: {function_name}")
            
            header_parts.append(f"Similarity: {1-distance:.3f}")
            
            context_parts.append(
                f"{'=' * 50}\n"
                f"{' | '.join(header_parts)}\n"
                f"{'=' * 50}\n"
                f"{doc}\n"
            )
        
        return "\n".join(context_parts)
    
    async def get_pipeline_status(self) -> Dict:
        """Get status of RAG pipeline components"""
        try:
            # Check vector store
            vectorstore_stats = await self.vectorstore_service.get_collection_stats()
            vectorstore_healthy = self.vectorstore_service.health_check()
            
            # Check embedding service
            embedding_dimension = self.embedding_service.get_embedding_dimension()
            
            return {
                "vectorstore_healthy": vectorstore_healthy,
                "total_chunks": vectorstore_stats.get('total_chunks', 0),
                "file_types": vectorstore_stats.get('file_types', {}),
                "embedding_dimension": embedding_dimension,
                "embedding_provider": self.embedding_service.embedding_provider,
                "is_ready": vectorstore_healthy and vectorstore_stats.get('total_chunks', 0) > 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get pipeline status: {str(e)}")
            return {
                "vectorstore_healthy": False,
                "total_chunks": 0,
                "file_types": {},
                "embedding_dimension": 0,
                "embedding_provider": "unknown",
                "is_ready": False,
                "error": str(e)
            }
    
    async def clear_knowledge_base(self) -> Dict:
        """Clear all documents from the knowledge base"""
        try:
            deleted_count = await self.vectorstore_service.clear_collection()
            
            return {
                "status": "success",
                "deleted_chunks": deleted_count,
                "message": f"Cleared {deleted_count} chunks from knowledge base"
            }
            
        except Exception as e:
            logger.error(f"Failed to clear knowledge base: {str(e)}")
            return {
                "status": "error",
                "deleted_chunks": 0,
                "message": f"Error clearing knowledge base: {str(e)}"
            }
    
    async def add_document(self, doc_id: str, content: str, metadata: Dict) -> Dict:
        """Add a document to the knowledge base"""
        try:
            # Handle CSV files specially
            if metadata.get('file_type') == '.csv':
                chunks = await self._process_csv_content(content, metadata)
            else:
                from app.services.chunking_service import ChunkingService
                
                # Initialize chunking service
                chunking_service = ChunkingService()
                
                # Chunk the document
                chunks = await chunking_service.chunk_document(
                    content=content,
                    metadata=metadata
                )
            
            if not chunks:
                logger.warning(f"No chunks generated for document {doc_id}")
                return {
                    "status": "warning",
                    "chunks_added": 0,
                    "message": "No chunks generated from document"
                }
            
            # Process each chunk
            chunks_added = 0
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}_chunk_{i}"
                
                # Generate embedding
                embedding = await self.embedding_service.embed_text(chunk['content'])
                
                # Add to vector store
                await self.vectorstore_service.add_document(
                    doc_id=chunk_id,
                    content=chunk['content'],
                    embedding=embedding,
                    metadata={**metadata, **chunk.get('metadata', {})}
                )
                
                chunks_added += 1
            
            logger.info(f"Added {chunks_added} chunks for document {doc_id}")
            
            return {
                "status": "success",
                "chunks_added": chunks_added,
                "message": f"Successfully added {chunks_added} chunks"
            }
            
        except Exception as e:
            logger.error(f"Failed to add document {doc_id}: {str(e)}")
            return {
                "status": "error",
                "chunks_added": 0,
                "message": f"Error adding document: {str(e)}"
            }
    
    async def _process_csv_content(self, content: str, metadata: Dict) -> List[Dict]:
        """Process CSV content into chunks"""
        chunks = []
        
        # Handle very large files by limiting content processing
        if len(content) > 10_000_000:  # 10MB limit for full processing
            return await self._process_large_csv_content(content, metadata)
        
        lines = content.strip().split('\n')
        
        if not lines:
            return chunks
        
        filename = metadata.get('file_name', 'unknown.csv')
        
        try:
            # Get header row
            header = lines[0] if lines else ""
            
            # For small CSV files (< 1000 rows), create summary chunks
            if len(lines) <= 1000:
                # Create header chunk
                columns_str = header if header else ""
                chunks.append({
                    'content': f"CSV File: {filename}\nColumns: {header}\nTotal Rows: {len(lines) - 1}",
                    'metadata': {
                        **metadata,
                        'chunk_type': 'csv_header',
                        'row_count': len(lines) - 1,
                        'columns_str': columns_str,
                        'column_count': len(header.split(',')) if header else 0
                    }
                })
                
                # Create sample data chunk (first 10 rows)
                sample_rows = lines[1:11] if len(lines) > 1 else []
                if sample_rows:
                    sample_content = f"Sample data from {filename}:\n{header}\n" + "\n".join(sample_rows)
                    chunks.append({
                        'content': sample_content,
                        'metadata': {
                            **metadata,
                            'chunk_type': 'csv_sample',
                            'sample_size': len(sample_rows)
                        }
                    })
            
            else:
                # For large CSV files, create summary and sample chunks
                # Header chunk
                columns_str = header if header else ""
                chunks.append({
                    'content': f"Large CSV File: {filename}\nColumns: {header}\nTotal Rows: {len(lines) - 1}",
                    'metadata': {
                        **metadata,
                        'chunk_type': 'csv_header_large',
                        'row_count': len(lines) - 1,
                        'columns_str': columns_str,
                        'column_count': len(header.split(',')) if header else 0
                    }
                })
                
                # Sample chunk from beginning
                sample_rows = lines[1:21] if len(lines) > 1 else []
                if sample_rows:
                    sample_content = f"Sample from {filename} (first 20 rows):\n{header}\n" + "\n".join(sample_rows)
                    chunks.append({
                        'content': sample_content,
                        'metadata': {
                            **metadata,
                            'chunk_type': 'csv_sample_large',
                            'sample_size': len(sample_rows)
                        }
                    })
                
                # Create a statistical summary
                stats_content = f"Statistics for {filename}:\n"
                stats_content += f"- Total records: {len(lines) - 1:,}\n"
                stats_content += f"- Columns: {len(header.split(',')) if header else 0}\n"
                stats_content += f"- File size: {metadata.get('file_size', 0):,} bytes\n"
                stats_content += f"- Data type: Large dataset suitable for analysis\n"
                
                chunks.append({
                    'content': stats_content,
                    'metadata': {
                        **metadata,
                        'chunk_type': 'csv_statistics',
                        'is_large_dataset': True
                    }
                })
            
        except Exception as e:
            logger.error(f"Error processing CSV {filename}: {str(e)}")
            # Fallback to simple text chunk
            chunks.append({
                'content': f"CSV File: {filename}\nContent preview:\n{content[:1000]}...",
                'metadata': {
                    **metadata,
                    'chunk_type': 'csv_fallback',
                    'processing_error': str(e)
                }
            })
        
        return chunks
    
    async def _process_large_csv_content(self, content: str, metadata: Dict) -> List[Dict]:
        """Process very large CSV files with limited memory usage"""
        chunks = []
        filename = metadata.get('file_name', 'unknown.csv')
        
        try:
            # Only read first 1000 characters to get header and sample
            preview_content = content[:1000]
            lines = preview_content.split('\n')
            
            if not lines:
                return chunks
            
            header = lines[0] if lines else ""
            columns_str = header if header else ""
            
            # Estimate total rows from file size (rough calculation)
            estimated_rows = len(content) // 100  # Rough estimate
            
            # Create header chunk for large file
            chunks.append({
                'content': f"Very Large CSV File: {filename}\nColumns: {header}\nEstimated Rows: ~{estimated_rows:,}\nFile Size: {len(content):,} bytes\nNote: This is a large dataset - only header and sample processed for performance.",
                'metadata': {
                    **metadata,
                    'chunk_type': 'csv_header_very_large',
                    'estimated_rows': estimated_rows,
                    'columns_str': columns_str,
                    'column_count': len(header.split(',')) if header else 0,
                    'file_size_bytes': len(content),
                    'is_large_dataset': True
                }
            })
            
            # Create sample chunk from first few lines
            sample_lines = lines[1:6] if len(lines) > 1 else []
            if sample_lines:
                sample_content = f"Sample from large CSV {filename}:\n{header}\n" + "\n".join(sample_lines)
                sample_content += f"\n\n... (File contains ~{estimated_rows:,} total rows)"
                
                chunks.append({
                    'content': sample_content,
                    'metadata': {
                        **metadata,
                        'chunk_type': 'csv_sample_very_large',
                        'sample_size': len(sample_lines),
                        'is_large_dataset': True
                    }
                })
            
        except Exception as e:
            logger.error(f"Error processing large CSV {filename}: {str(e)}")
            # Fallback chunk
            chunks.append({
                'content': f"Large CSV File: {filename}\nFile Size: {len(content):,} bytes\nProcessing limited due to size.",
                'metadata': {
                    **metadata,
                    'chunk_type': 'csv_large_fallback',
                    'processing_error': str(e),
                    'file_size_bytes': len(content)
                }
            })
        
        return chunks
