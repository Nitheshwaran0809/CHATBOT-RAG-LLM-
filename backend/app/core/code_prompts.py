"""
Specialized prompts for code assistant features
Context-aware prompts for different coding tasks
"""

from typing import List, Dict, Any

# Enhanced system prompt for code generation
ENHANCED_CODE_ASSISTANT_PROMPT = """
You are an expert software engineer and code assistant with deep knowledge of software architecture, design patterns, and best practices. You have access to the user's project codebase and can provide intelligent, context-aware assistance.

## Your Core Capabilities:

### 1. Code Generation & Completion
- Generate new code that seamlessly integrates with existing codebase
- Follow established patterns, naming conventions, and architectural decisions
- Respect existing dependencies, imports, and project structure
- Write production-ready, well-documented code with proper error handling

### 2. Debugging & Problem Solving  
- Analyze errors against the codebase context
- Identify root causes by examining related files and dependencies
- Suggest specific fixes with line-by-line explanations
- Recommend preventive measures and code improvements

### 3. Architecture & Design Guidance
- Suggest appropriate design patterns for the current architecture
- Recommend refactoring opportunities while maintaining compatibility
- Advise on scalability, performance, and maintainability improvements
- Help with API design, database schema, and system integration

### 4. Code Review & Best Practices
- Review code for bugs, security issues, and performance problems
- Suggest improvements following language-specific best practices
- Recommend testing strategies and implementation approaches
- Ensure code follows project conventions and standards

## Context Analysis Guidelines:

When provided with code context, analyze:
- **Project Structure**: Understand the overall architecture and organization
- **Dependencies**: Identify frameworks, libraries, and external services used
- **Patterns**: Recognize existing design patterns and coding conventions
- **Data Flow**: Understand how data moves through the application
- **Configuration**: Consider environment settings and deployment requirements

## Response Format:

1. **Understanding**: Briefly acknowledge what you understand about the request
2. **Context Analysis**: Explain relevant patterns/conventions found in the codebase
3. **Solution**: Provide the requested code/guidance with clear explanations
4. **Integration Notes**: Explain how the solution fits with existing code
5. **Additional Considerations**: Suggest related improvements or considerations

## Code Quality Standards:

- Write clean, readable, and maintainable code
- Include appropriate comments and documentation
- Handle edge cases and error conditions
- Follow security best practices
- Optimize for performance when relevant
- Ensure backward compatibility when modifying existing code

Remember: You're not just generating code, you're helping build and maintain a cohesive, professional software system.
"""

def build_code_generation_prompt(
    context: str,
    request: str,
    conversation_history: List[Dict],
    project_info: Dict[str, Any] = None
) -> str:
    """Build specialized prompt for code generation tasks"""
    
    # Analyze request type
    request_lower = request.lower()
    task_type = "general"
    
    if any(word in request_lower for word in ["create", "generate", "write", "implement", "build"]):
        task_type = "generation"
    elif any(word in request_lower for word in ["fix", "debug", "error", "bug", "issue", "problem"]):
        task_type = "debugging"
    elif any(word in request_lower for word in ["review", "improve", "optimize", "refactor"]):
        task_type = "review"
    elif any(word in request_lower for word in ["explain", "how", "what", "why", "understand"]):
        task_type = "explanation"
    
    # Build context analysis
    context_analysis = _analyze_code_context(context)
    
    # Build conversation context
    history_text = ""
    if conversation_history:
        for msg in conversation_history[-3:]:  # Last 3 exchanges
            role = "User" if msg['role'] == 'user' else "Assistant"
            history_text += f"{role}: {msg['content'][:200]}...\n\n"
    
    # Task-specific instructions
    task_instructions = {
        "generation": """
## Code Generation Task
Focus on:
- Following existing patterns and conventions
- Integrating seamlessly with current architecture
- Including proper error handling and validation
- Adding appropriate documentation and comments
- Considering scalability and maintainability
""",
        "debugging": """
## Debugging Task
Focus on:
- Identifying the root cause of the issue
- Analyzing error context against the codebase
- Providing specific, actionable fixes
- Explaining why the error occurred
- Suggesting prevention strategies
""",
        "review": """
## Code Review Task
Focus on:
- Identifying potential bugs and security issues
- Suggesting performance improvements
- Recommending best practices
- Ensuring code follows project conventions
- Proposing refactoring opportunities
""",
        "explanation": """
## Code Explanation Task
Focus on:
- Breaking down complex concepts clearly
- Relating explanations to the existing codebase
- Providing practical examples
- Highlighting important patterns and practices
- Connecting to broader architectural decisions
"""
    }
    
    return f"""{ENHANCED_CODE_ASSISTANT_PROMPT}

{task_instructions.get(task_type, "")}

## Project Context Analysis
{context_analysis}

## Relevant Code from Project
{context}

## Recent Conversation
{history_text}

## Current Request
User: {request}

## Instructions
Provide a comprehensive response that addresses the user's request while considering the project context and maintaining consistency with existing code patterns. Be specific, practical, and include code examples when appropriate.

Response Format:
1. **Analysis**: What I understand from your request and the codebase
2. **Solution**: The code/guidance you requested with explanations
3. **Integration**: How this fits with your existing code
4. **Next Steps**: Suggested follow-up actions or improvements
"""

def _analyze_code_context(context: str) -> str:
    """Analyze the provided code context to understand project patterns"""
    
    analysis_parts = []
    
    # Detect frameworks and libraries
    frameworks = []
    if "fastapi" in context.lower() or "from fastapi" in context.lower():
        frameworks.append("FastAPI")
    if "streamlit" in context.lower() or "import streamlit" in context.lower():
        frameworks.append("Streamlit")
    if "django" in context.lower():
        frameworks.append("Django")
    if "flask" in context.lower():
        frameworks.append("Flask")
    if "react" in context.lower() or "jsx" in context.lower():
        frameworks.append("React")
    if "vue" in context.lower():
        frameworks.append("Vue.js")
    if "express" in context.lower() and "javascript" in context.lower():
        frameworks.append("Express.js")
    
    if frameworks:
        analysis_parts.append(f"**Frameworks Detected**: {', '.join(frameworks)}")
    
    # Detect programming languages
    languages = []
    if "def " in context or "import " in context or "class " in context:
        languages.append("Python")
    if "function " in context or "const " in context or "=>" in context:
        languages.append("JavaScript/TypeScript")
    if "public class" in context or "private " in context:
        languages.append("Java")
    if "#include" in context or "int main" in context:
        languages.append("C/C++")
    if "func " in context or "package main" in context:
        languages.append("Go")
    
    if languages:
        analysis_parts.append(f"**Languages**: {', '.join(languages)}")
    
    # Detect architectural patterns
    patterns = []
    if "router" in context.lower() or "endpoint" in context.lower():
        patterns.append("REST API")
    if "service" in context.lower() and "class" in context.lower():
        patterns.append("Service Layer Pattern")
    if "repository" in context.lower() or "dao" in context.lower():
        patterns.append("Repository Pattern")
    if "middleware" in context.lower():
        patterns.append("Middleware Pattern")
    if "async def" in context or "await " in context:
        patterns.append("Async/Await Pattern")
    
    if patterns:
        analysis_parts.append(f"**Patterns**: {', '.join(patterns)}")
    
    # Detect database usage
    databases = []
    if "postgresql" in context.lower() or "psycopg2" in context.lower():
        databases.append("PostgreSQL")
    if "mysql" in context.lower():
        databases.append("MySQL")
    if "mongodb" in context.lower() or "pymongo" in context.lower():
        databases.append("MongoDB")
    if "sqlite" in context.lower():
        databases.append("SQLite")
    if "redis" in context.lower():
        databases.append("Redis")
    if "chromadb" in context.lower():
        databases.append("ChromaDB")
    
    if databases:
        analysis_parts.append(f"**Databases**: {', '.join(databases)}")
    
    # Detect testing frameworks
    testing = []
    if "pytest" in context.lower() or "def test_" in context:
        testing.append("pytest")
    if "unittest" in context.lower() or "TestCase" in context:
        testing.append("unittest")
    if "jest" in context.lower() or "describe(" in context:
        testing.append("Jest")
    
    if testing:
        analysis_parts.append(f"**Testing**: {', '.join(testing)}")
    
    # Detect configuration management
    config = []
    if "pydantic" in context.lower() or "BaseSettings" in context:
        config.append("Pydantic Settings")
    if "os.getenv" in context or "environment" in context.lower():
        config.append("Environment Variables")
    if "config.json" in context.lower() or "settings.py" in context.lower():
        config.append("Configuration Files")
    
    if config:
        analysis_parts.append(f"**Configuration**: {', '.join(config)}")
    
    return "\n".join(analysis_parts) if analysis_parts else "**Context**: General code analysis"

def build_debugging_prompt(
    context: str,
    error_message: str,
    conversation_history: List[Dict]
) -> str:
    """Build specialized prompt for debugging tasks"""
    
    context_analysis = _analyze_code_context(context)
    
    return f"""{ENHANCED_CODE_ASSISTANT_PROMPT}

## Debugging Task
You are helping debug an issue. Focus on:
- Analyzing the error message in context of the codebase
- Identifying the root cause
- Providing specific, actionable fixes
- Explaining why the error occurred
- Suggesting prevention strategies

## Project Context Analysis
{context_analysis}

## Relevant Code from Project
{context}

## Error Information
{error_message}

## Instructions
1. **Error Analysis**: Explain what the error means and why it's occurring
2. **Root Cause**: Identify the underlying issue in the code
3. **Fix**: Provide specific code changes to resolve the issue
4. **Prevention**: Suggest how to prevent similar issues in the future
"""

def build_architecture_prompt(
    context: str,
    request: str,
    conversation_history: List[Dict]
) -> str:
    """Build specialized prompt for architecture and design questions"""
    
    context_analysis = _analyze_code_context(context)
    
    return f"""{ENHANCED_CODE_ASSISTANT_PROMPT}

## Architecture & Design Task
You are providing architectural guidance. Focus on:
- Understanding the current system architecture
- Suggesting improvements that fit the existing patterns
- Recommending scalable and maintainable solutions
- Considering performance, security, and best practices

## Project Context Analysis
{context_analysis}

## Relevant Code from Project
{context}

## Architecture Request
{request}

## Instructions
1. **Current Architecture**: Analyze the existing system design
2. **Recommendations**: Suggest specific architectural improvements
3. **Implementation**: Provide concrete steps and code examples
4. **Trade-offs**: Discuss benefits and potential challenges
"""

def build_code_review_prompt(
    context: str,
    code_to_review: str,
    conversation_history: List[Dict]
) -> str:
    """Build specialized prompt for code review tasks"""
    
    context_analysis = _analyze_code_context(context)
    
    return f"""{ENHANCED_CODE_ASSISTANT_PROMPT}

## Code Review Task
You are conducting a thorough code review. Focus on:
- Identifying bugs, security issues, and performance problems
- Checking adherence to project conventions and best practices
- Suggesting improvements for readability and maintainability
- Ensuring proper error handling and edge case coverage

## Project Context Analysis
{context_analysis}

## Existing Codebase Context
{context}

## Code to Review
{code_to_review}

## Instructions
Provide a comprehensive code review covering:
1. **Issues Found**: Bugs, security concerns, performance problems
2. **Best Practices**: Adherence to coding standards and conventions
3. **Improvements**: Suggestions for better code quality
4. **Positive Aspects**: What's done well in the code
"""
