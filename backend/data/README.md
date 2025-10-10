# Manual Data Directory

This directory is for manually adding project files that will be processed by the RAG system.

## Structure

```
data/
├── src/           # Source code files
├── config/        # Configuration files  
├── docs/          # Documentation files
└── README.md      # This file
```

## Supported File Types

- **Code**: .py, .js, .ts, .java, .cpp, .go, .rs, etc.
- **Config**: .json, .yaml, .toml, .ini, .xml
- **Docs**: .md, .txt, .rst
- **Web**: .html, .css, .scss

## Usage

1. Add your project files to appropriate subdirectories
2. Restart the backend container to process new files
3. Use Code Assistant mode to query your project data

## Example

```
data/
├── src/
│   ├── main.py
│   ├── utils.py
│   └── models/
│       └── user.py
├── config/
│   ├── settings.json
│   └── database.yaml
└── docs/
    ├── README.md
    └── api.md
```
