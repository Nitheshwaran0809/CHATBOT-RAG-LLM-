# File types supported for upload and processing
ACCEPTED_FILE_TYPES = {
    # Code files
    'code': ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', 
             '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala'],
    
    # Config files
    'config': ['.json', '.yaml', '.yml', '.toml', '.ini', '.env.example', 
               '.conf', '.xml', '.properties'],
    
    # Documentation
    'docs': ['.md', '.txt', '.rst', '.pdf', '.docx'],
    
    # Database
    'database': ['.sql', '.db'],
    
    # Web
    'web': ['.html', '.css', '.scss', '.sass'],
    
    # Data
    'data': ['.csv', '.xlsx'],
    
    # Scripts
    'scripts': ['.sh', '.bat', '.ps1'],
    
    # Docker/CI
    'devops': ['Dockerfile', '.dockerignore', '.gitlab-ci.yml', '.github']
}

# Flatten all file types for easy checking
ALL_SUPPORTED_EXTENSIONS = []
for category in ACCEPTED_FILE_TYPES.values():
    ALL_SUPPORTED_EXTENSIONS.extend(category)

# Language mapping for syntax highlighting and parsing
LANGUAGE_MAPPING = {
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.jsx': 'javascript',
    '.tsx': 'typescript',
    '.java': 'java',
    '.cpp': 'cpp',
    '.c': 'c',
    '.h': 'c',
    '.go': 'go',
    '.rs': 'rust',
    '.rb': 'ruby',
    '.php': 'php',
    '.swift': 'swift',
    '.kt': 'kotlin',
    '.scala': 'scala',
    '.html': 'html',
    '.css': 'css',
    '.scss': 'scss',
    '.sass': 'sass',
    '.sql': 'sql',
    '.json': 'json',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.toml': 'toml',
    '.xml': 'xml',
    '.md': 'markdown',
    '.txt': 'text',
    '.sh': 'bash',
    '.bat': 'batch',
    '.ps1': 'powershell'
}

# Chunking parameters by file type
CHUNKING_CONFIG = {
    'code': {
        'max_tokens': 1000,
        'overlap_tokens': 100,
        'preserve_structure': True
    },
    'docs': {
        'max_tokens': 500,
        'overlap_tokens': 50,
        'preserve_structure': False
    },
    'config': {
        'max_tokens': 800,
        'overlap_tokens': 0,
        'preserve_structure': True
    },
    'data': {
        'max_tokens': 300,
        'overlap_tokens': 0,
        'preserve_structure': False
    }
}
