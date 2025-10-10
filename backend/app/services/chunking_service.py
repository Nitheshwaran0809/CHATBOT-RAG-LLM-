import re
from typing import List, Dict, Any
import logging
from app.core.constants import LANGUAGE_MAPPING, CHUNKING_CONFIG

logger = logging.getLogger(__name__)

class ChunkingService:
    """
    Different chunking strategies for different file types.
    Intelligent chunking that preserves code structure and document flow.
    """
    
    def __init__(self):
        self.max_chunk_size = 1000  # tokens (approximate)
        self.overlap_size = 100     # tokens (approximate)
    
    async def chunk_document(
        self, 
        content: str, 
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Main chunking method that routes to appropriate strategy
        """
        file_type = metadata.get('file_type', '.txt')
        filename = metadata.get('filename', 'unknown')
        
        try:
            if file_type in ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', 
                           '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala']:
                return await self.chunk_code(content, metadata)
            elif file_type in ['.json', '.yaml', '.yml', '.toml', '.ini', '.xml', '.properties']:
                return await self.chunk_config(content, metadata)
            elif file_type in ['.md', '.txt', '.rst']:
                return await self.chunk_document_text(content, metadata)
            elif file_type == '.sql':
                return await self.chunk_sql(content, metadata)
            elif file_type in ['.html', '.css', '.scss', '.sass']:
                return await self.chunk_web(content, metadata)
            elif file_type == '.csv':
                return await self.chunk_csv(content, metadata)
            else:
                # Default chunking for unknown types
                return await self.chunk_generic(content, metadata)
                
        except Exception as e:
            logger.error(f"Error chunking {filename}: {str(e)}")
            # Fallback to generic chunking
            return await self.chunk_generic(content, metadata)
    
    async def chunk_code(
        self, 
        content: str, 
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Chunk code files by functions/classes when possible
        Falls back to line-based chunking for complex cases
        """
        filename = metadata.get('filename', 'unknown')
        file_type = metadata.get('file_type', '.py')
        language = LANGUAGE_MAPPING.get(file_type, 'text')
        
        chunks = []
        
        try:
            # Try to use tree-sitter for AST-based chunking
            ast_chunks = await self._chunk_with_ast(content, language, metadata)
            if ast_chunks:
                return ast_chunks
        except Exception as e:
            logger.warning(f"AST chunking failed for {filename}, falling back to regex: {str(e)}")
        
        # Fallback to regex-based function detection
        try:
            regex_chunks = await self._chunk_with_regex(content, language, metadata)
            if regex_chunks:
                return regex_chunks
        except Exception as e:
            logger.warning(f"Regex chunking failed for {filename}, falling back to line-based: {str(e)}")
        
        # Final fallback to line-based chunking
        return await self._chunk_by_lines(content, metadata, preserve_structure=True)
    
    async def _chunk_with_ast(
        self, 
        content: str, 
        language: str, 
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Use tree-sitter for AST-based chunking (when available)
        """
        try:
            import tree_sitter_languages
            
            # Get language parser
            parser = tree_sitter_languages.get_parser(language)
            if not parser:
                return []
                
            # Parse the code
            tree = parser.parse(bytes(content, 'utf8'))
            
            chunks = []
            lines = content.split('\n')
            
            # Extract functions and classes
            for node in tree.root_node.children:
                if node.type in ['function_definition', 'method_definition', 'class_definition', 
                               'function_declaration', 'method_declaration']:
                    
                    start_line = node.start_point[0]
                    end_line = node.end_point[0]
                    
                    # Extract the code for this node
                    node_lines = lines[start_line:end_line + 1]
                    node_content = '\n'.join(node_lines)
                    
                    # Get function/class name
                    name_node = None
                    for child in node.children:
                        if child.type == 'identifier':
                            name_node = child
                            break
                    
                    function_name = ""
                    if name_node:
                        function_name = content[name_node.start_byte:name_node.end_byte]
                    
                    chunk_metadata = metadata.copy()
                    chunk_metadata.update({
                        'start_line': start_line + 1,
                        'end_line': end_line + 1,
                        'function_name': function_name,
                        'node_type': node.type,
                        'chunk_type': 'ast_function'
                    })
                    
                    chunks.append({
                        'content': node_content,
                        'metadata': chunk_metadata
                    })
            
            # If we found functions/classes, also add imports and global code
            if chunks:
                # Add imports and global code at the beginning
                global_lines = []
                current_line = 0
                
                for chunk in chunks:
                    start = chunk['metadata']['start_line'] - 1
                    if current_line < start:
                        global_lines.extend(lines[current_line:start])
                    current_line = chunk['metadata']['end_line']
                
                # Add remaining lines
                if current_line < len(lines):
                    global_lines.extend(lines[current_line:])
                
                if global_lines:
                    global_content = '\n'.join(global_lines).strip()
                    if global_content:
                        global_metadata = metadata.copy()
                        global_metadata.update({
                            'chunk_type': 'ast_global',
                            'start_line': 1,
                            'end_line': len(lines)
                        })
                        
                        chunks.insert(0, {
                            'content': global_content,
                            'metadata': global_metadata
                        })
            
            return chunks
            
        except ImportError:
            logger.warning("tree-sitter-languages not available, skipping AST chunking")
            return []
        except Exception as e:
            logger.error(f"AST chunking error: {str(e)}")
            return []
    
    async def _chunk_with_regex(
        self, 
        content: str, 
        language: str, 
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Use regex patterns to detect functions/classes
        """
        chunks = []
        lines = content.split('\n')
        
        # Language-specific regex patterns
        patterns = {
            'python': [
                r'^(def\s+\w+.*?:)',
                r'^(class\s+\w+.*?:)',
                r'^(async\s+def\s+\w+.*?:)'
            ],
            'javascript': [
                r'^(function\s+\w+.*?\{)',
                r'^(const\s+\w+\s*=\s*.*?=>)',
                r'^(class\s+\w+.*?\{)'
            ],
            'java': [
                r'^(\s*public\s+.*?\{)',
                r'^(\s*private\s+.*?\{)',
                r'^(\s*protected\s+.*?\{)',
                r'^(\s*class\s+\w+.*?\{)'
            ]
        }
        
        if language not in patterns:
            return []
        
        # Find function/class boundaries
        boundaries = []
        for i, line in enumerate(lines):
            for pattern in patterns[language]:
                if re.match(pattern, line.strip()):
                    boundaries.append(i)
                    break
        
        if not boundaries:
            return []
        
        # Create chunks based on boundaries
        for i, start in enumerate(boundaries):
            end = boundaries[i + 1] if i + 1 < len(boundaries) else len(lines)
            
            chunk_lines = lines[start:end]
            chunk_content = '\n'.join(chunk_lines)
            
            # Extract function name
            first_line = chunk_lines[0].strip()
            function_name = self._extract_function_name(first_line, language)
            
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                'start_line': start + 1,
                'end_line': end,
                'function_name': function_name,
                'chunk_type': 'regex_function'
            })
            
            chunks.append({
                'content': chunk_content,
                'metadata': chunk_metadata
            })
        
        return chunks
    
    def _extract_function_name(self, line: str, language: str) -> str:
        """Extract function name from the first line"""
        if language == 'python':
            match = re.search(r'def\s+(\w+)', line)
            if match:
                return match.group(1)
            match = re.search(r'class\s+(\w+)', line)
            if match:
                return match.group(1)
        elif language == 'javascript':
            match = re.search(r'function\s+(\w+)', line)
            if match:
                return match.group(1)
            match = re.search(r'const\s+(\w+)', line)
            if match:
                return match.group(1)
        elif language == 'java':
            match = re.search(r'class\s+(\w+)', line)
            if match:
                return match.group(1)
            match = re.search(r'\w+\s+(\w+)\s*\(', line)
            if match:
                return match.group(1)
        
        return ""
    
    async def chunk_config(
        self, 
        content: str, 
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Chunk configuration files intelligently
        """
        # For small configs, keep as single chunk
        if len(content) < 2000:
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                'chunk_type': 'config_complete',
                'start_line': 1,
                'end_line': len(content.split('\n'))
            })
            
            return [{
                'content': content,
                'metadata': chunk_metadata
            }]
        
        # For large configs, split by top-level sections
        return await self._chunk_by_lines(content, metadata, chunk_size=800)
    
    async def chunk_document_text(
        self, 
        content: str, 
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Chunk markdown and text documents by sections/paragraphs
        """
        file_type = metadata.get('file_type', '.txt')
        
        if file_type == '.md':
            return await self._chunk_markdown(content, metadata)
        else:
            return await self._chunk_by_paragraphs(content, metadata)
    
    async def _chunk_markdown(
        self, 
        content: str, 
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Chunk markdown by headers and sections
        """
        chunks = []
        lines = content.split('\n')
        
        # Find header boundaries
        header_indices = []
        for i, line in enumerate(lines):
            if re.match(r'^#{1,6}\s+', line):
                header_indices.append(i)
        
        if not header_indices:
            # No headers, chunk by paragraphs
            return await self._chunk_by_paragraphs(content, metadata)
        
        # Create chunks based on headers
        for i, start in enumerate(header_indices):
            end = header_indices[i + 1] if i + 1 < len(header_indices) else len(lines)
            
            section_lines = lines[start:end]
            section_content = '\n'.join(section_lines)
            
            # Extract section title
            header_line = section_lines[0]
            section_title = re.sub(r'^#+\s*', '', header_line)
            
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                'start_line': start + 1,
                'end_line': end,
                'section_title': section_title,
                'chunk_type': 'markdown_section'
            })
            
            chunks.append({
                'content': section_content,
                'metadata': chunk_metadata
            })
        
        return chunks
    
    async def _chunk_by_paragraphs(
        self, 
        content: str, 
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Chunk text by paragraphs with overlap
        """
        paragraphs = re.split(r'\n\s*\n', content)
        chunks = []
        current_chunk = []
        current_size = 0
        
        for para in paragraphs:
            para_size = len(para.split())
            
            if current_size + para_size > self.max_chunk_size and current_chunk:
                # Create chunk
                chunk_content = '\n\n'.join(current_chunk)
                chunk_metadata = metadata.copy()
                chunk_metadata.update({
                    'chunk_type': 'paragraph_group',
                    'paragraph_count': len(current_chunk)
                })
                
                chunks.append({
                    'content': chunk_content,
                    'metadata': chunk_metadata
                })
                
                # Start new chunk with overlap
                if self.overlap_size > 0 and current_chunk:
                    current_chunk = current_chunk[-1:]  # Keep last paragraph for overlap
                    current_size = len(current_chunk[0].split())
                else:
                    current_chunk = []
                    current_size = 0
            
            current_chunk.append(para)
            current_size += para_size
        
        # Add final chunk
        if current_chunk:
            chunk_content = '\n\n'.join(current_chunk)
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                'chunk_type': 'paragraph_group',
                'paragraph_count': len(current_chunk)
            })
            
            chunks.append({
                'content': chunk_content,
                'metadata': chunk_metadata
            })
        
        return chunks
    
    async def chunk_sql(
        self, 
        content: str, 
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Chunk SQL by statements
        """
        # Split by SQL statements (basic approach)
        statements = re.split(r';\s*\n', content)
        chunks = []
        
        for i, statement in enumerate(statements):
            statement = statement.strip()
            if not statement:
                continue
            
            # Detect statement type
            statement_type = "UNKNOWN"
            if re.match(r'^\s*CREATE\s+TABLE', statement, re.IGNORECASE):
                statement_type = "CREATE_TABLE"
            elif re.match(r'^\s*CREATE\s+INDEX', statement, re.IGNORECASE):
                statement_type = "CREATE_INDEX"
            elif re.match(r'^\s*INSERT', statement, re.IGNORECASE):
                statement_type = "INSERT"
            elif re.match(r'^\s*SELECT', statement, re.IGNORECASE):
                statement_type = "SELECT"
            
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                'statement_type': statement_type,
                'statement_index': i + 1,
                'chunk_type': 'sql_statement'
            })
            
            chunks.append({
                'content': statement,
                'metadata': chunk_metadata
            })
        
        return chunks
    
    async def chunk_web(
        self, 
        content: str, 
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Chunk HTML/CSS files
        """
        return await self._chunk_by_lines(content, metadata, chunk_size=800)
    
    async def chunk_generic(
        self, 
        content: str, 
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generic chunking for unknown file types
        """
        return await self._chunk_by_lines(content, metadata)
    
    async def _chunk_by_lines(
        self, 
        content: str, 
        metadata: Dict[str, Any], 
        chunk_size: int = None,
        preserve_structure: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Chunk content by lines with approximate token limits
        """
        if chunk_size is None:
            chunk_size = self.max_chunk_size
        
        lines = content.split('\n')
        chunks = []
        current_chunk = []
        current_size = 0
        
        for i, line in enumerate(lines):
            line_size = len(line.split())
            
            if current_size + line_size > chunk_size and current_chunk:
                # Create chunk
                chunk_content = '\n'.join(current_chunk)
                chunk_metadata = metadata.copy()
                chunk_metadata.update({
                    'start_line': i - len(current_chunk) + 1,
                    'end_line': i,
                    'chunk_type': 'line_based',
                    'line_count': len(current_chunk)
                })
                
                chunks.append({
                    'content': chunk_content,
                    'metadata': chunk_metadata
                })
                
                # Start new chunk
                current_chunk = []
                current_size = 0
            
            current_chunk.append(line)
            current_size += line_size
        
        # Add final chunk
        if current_chunk:
            chunk_content = '\n'.join(current_chunk)
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                'start_line': len(lines) - len(current_chunk) + 1,
                'end_line': len(lines),
                'chunk_type': 'line_based',
                'line_count': len(current_chunk)
            })
            
            chunks.append({
                'content': chunk_content,
                'metadata': chunk_metadata
            })
        
        return chunks
