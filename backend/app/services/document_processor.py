import os
import chardet
from pathlib import Path
from typing import Tuple, Dict, Any
import logging

# Try to import magic, but don't fail if not available
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    magic = None

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """
    Route files to appropriate processors based on type.
    Extract text content from various formats.
    """
    
    def __init__(self):
        self.handlers = {
            # Code files
            '.py': self._process_code,
            '.js': self._process_code,
            '.ts': self._process_code,
            '.jsx': self._process_code,
            '.tsx': self._process_code,
            '.java': self._process_code,
            '.cpp': self._process_code,
            '.c': self._process_code,
            '.h': self._process_code,
            '.go': self._process_code,
            '.rs': self._process_code,
            '.rb': self._process_code,
            '.php': self._process_code,
            '.swift': self._process_code,
            '.kt': self._process_code,
            '.scala': self._process_code,
            
            # Web files
            '.html': self._process_code,
            '.css': self._process_code,
            '.scss': self._process_code,
            '.sass': self._process_code,
            
            # Config files
            '.json': self._process_config,
            '.yaml': self._process_config,
            '.yml': self._process_config,
            '.toml': self._process_config,
            '.ini': self._process_config,
            '.xml': self._process_config,
            '.properties': self._process_config,
            
            # Documentation
            '.md': self._process_markdown,
            '.txt': self._process_text,
            '.rst': self._process_text,
            '.pdf': self._process_pdf,
            '.docx': self._process_docx,
            
            # Database
            '.sql': self._process_sql,
            
            # Data files
            '.csv': self._process_csv,
            '.xlsx': self._process_excel,
            
            # Scripts
            '.sh': self._process_code,
            '.bat': self._process_code,
            '.ps1': self._process_code,
        }
    
    async def process_file(
        self, 
        file_path: str, 
        filename: str
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Process file and return (text_content, metadata)
        """
        try:
            ext = Path(filename).suffix.lower()
            
            # Handle special cases (files without extensions)
            if not ext:
                if filename.lower() in ['dockerfile', 'makefile', 'readme']:
                    ext = '.txt'
                elif filename.startswith('.'):
                    ext = '.txt'
                else:
                    raise ValueError(f"Unknown file type: {filename}")
            
            if ext not in self.handlers:
                raise ValueError(f"Unsupported file type: {ext}")
            
            # Detect encoding for text files
            encoding = self._detect_encoding(file_path)
            
            # Route to appropriate handler
            content = await self.handlers[ext](file_path, encoding)
            
            # Build metadata
            metadata = {
                'filename': filename,
                'file_type': ext,
                'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                'encoding': encoding,
                'processed_at': None  # Will be set when adding to vector store
            }
            
            return content, metadata
            
        except Exception as e:
            logger.error(f"Error processing file {filename}: {str(e)}")
            raise
    
    def _detect_encoding(self, file_path: str) -> str:
        """Detect file encoding"""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # Read first 10KB
                result = chardet.detect(raw_data)
                encoding = result.get('encoding', 'utf-8')
                
                # Fallback to common encodings
                if not encoding or result.get('confidence', 0) < 0.7:
                    for fallback in ['utf-8', 'latin-1', 'cp1252']:
                        try:
                            with open(file_path, 'r', encoding=fallback) as test_file:
                                test_file.read(1000)
                            return fallback
                        except UnicodeDecodeError:
                            continue
                    return 'utf-8'  # Final fallback
                
                return encoding
                
        except Exception:
            return 'utf-8'
    
    async def _process_code(self, file_path: str, encoding: str) -> str:
        """Read code file, preserve structure"""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            # Basic validation
            if not content.strip():
                return "# Empty file"
            
            return content
            
        except Exception as e:
            logger.error(f"Error reading code file {file_path}: {str(e)}")
            return f"# Error reading file: {str(e)}"
    
    async def _process_config(self, file_path: str, encoding: str) -> str:
        """Process configuration files"""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            # Add context for config files
            ext = Path(file_path).suffix.lower()
            config_type = {
                '.json': 'JSON Configuration',
                '.yaml': 'YAML Configuration',
                '.yml': 'YAML Configuration',
                '.toml': 'TOML Configuration',
                '.ini': 'INI Configuration',
                '.xml': 'XML Configuration',
                '.properties': 'Properties Configuration'
            }.get(ext, 'Configuration')
            
            return f"# {config_type} File\n\n{content}"
            
        except Exception as e:
            logger.error(f"Error reading config file {file_path}: {str(e)}")
            return f"# Error reading configuration: {str(e)}"
    
    async def _process_markdown(self, file_path: str, encoding: str) -> str:
        """Process Markdown files"""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            return content
            
        except Exception as e:
            logger.error(f"Error reading markdown file {file_path}: {str(e)}")
            return f"# Error reading markdown: {str(e)}"
    
    async def _process_text(self, file_path: str, encoding: str) -> str:
        """Process plain text files"""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            return content
            
        except Exception as e:
            logger.error(f"Error reading text file {file_path}: {str(e)}")
            return f"Error reading text file: {str(e)}"
    
    async def _process_pdf(self, file_path: str, encoding: str) -> str:
        """Extract text from PDF using PyPDF2"""
        try:
            import PyPDF2
            
            text_parts = []
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                
                for page_num, page in enumerate(reader.pages, 1):
                    page_text = page.extract_text()
                    if page_text.strip():
                        text_parts.append(f"=== Page {page_num} ===\n{page_text}")
            
            return "\n\n".join(text_parts) if text_parts else "# Empty PDF or text extraction failed"
            
        except ImportError:
            return "# PDF processing requires PyPDF2 library"
        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {str(e)}")
            return f"# Error reading PDF: {str(e)}"
    
    async def _process_docx(self, file_path: str, encoding: str) -> str:
        """Extract text from Word document"""
        try:
            from docx import Document
            
            doc = Document(file_path)
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            
            return "\n\n".join(paragraphs) if paragraphs else "# Empty document"
            
        except ImportError:
            return "# DOCX processing requires python-docx library"
        except Exception as e:
            logger.error(f"Error reading DOCX {file_path}: {str(e)}")
            return f"# Error reading DOCX: {str(e)}"
    
    async def _process_sql(self, file_path: str, encoding: str) -> str:
        """Process SQL files"""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            return f"-- SQL Database Script\n\n{content}"
            
        except Exception as e:
            logger.error(f"Error reading SQL file {file_path}: {str(e)}")
            return f"-- Error reading SQL: {str(e)}"
    
    async def _process_csv(self, file_path: str, encoding: str) -> str:
        """Process CSV files - extract schema and sample data"""
        try:
            import pandas as pd
            
            # Read CSV with pandas
            df = pd.read_csv(file_path, encoding=encoding)
            
            # Create summary
            summary_parts = [
                f"# CSV Data File",
                f"Rows: {len(df)}",
                f"Columns: {len(df.columns)}",
                "",
                "## Schema",
                f"Columns: {', '.join(df.columns.tolist())}",
                "",
                f"Data types:\n{df.dtypes.to_string()}",
                "",
                "## Sample Data (first 5 rows)",
                df.head().to_string(index=False)
            ]
            
            return "\n".join(summary_parts)
            
        except ImportError:
            return "# CSV processing requires pandas library"
        except Exception as e:
            logger.error(f"Error reading CSV {file_path}: {str(e)}")
            return f"# Error reading CSV: {str(e)}"
    
    async def _process_excel(self, file_path: str, encoding: str) -> str:
        """Process Excel files - extract schema and sample data"""
        try:
            import pandas as pd
            
            # Read Excel file
            excel_file = pd.ExcelFile(file_path)
            
            summary_parts = [f"# Excel File"]
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                summary_parts.extend([
                    f"## Sheet: {sheet_name}",
                    f"Rows: {len(df)}",
                    f"Columns: {len(df.columns)}",
                    f"Columns: {', '.join(df.columns.tolist())}",
                    "",
                    "### Sample Data (first 3 rows)",
                    df.head(3).to_string(index=False),
                    ""
                ])
            
            return "\n".join(summary_parts)
            
        except ImportError:
            return "# Excel processing requires pandas and openpyxl libraries"
        except Exception as e:
            logger.error(f"Error reading Excel {file_path}: {str(e)}")
            return f"# Error reading Excel: {str(e)}"
