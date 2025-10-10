from typing import List, Dict

GENERAL_CHAT_SYSTEM_PROMPT = """
You are a helpful AI assistant. Engage in natural conversation,
answer questions accurately, and provide thoughtful responses.
Be concise but thorough.
"""

CODE_ASSISTANT_SYSTEM_PROMPT = """
You are an expert software engineer assistant with access to the user's project codebase.

Your responsibilities:
1. **Code Generation**: Generate new code that matches the existing project's patterns, style, and architecture
2. **Debugging**: Analyze errors against the codebase context and provide specific fixes
3. **Technical Guidance**: Answer questions about database connections, API integrations, best practices
4. **Code Review**: Suggest improvements while respecting existing conventions

Guidelines:
- Always check the provided context for existing patterns, naming conventions, and architecture
- Generate complete, runnable code snippets that fit seamlessly into the project
- When you see an error, analyze it against the codebase context
- Provide clear explanations with your code
- If context is insufficient, ask clarifying questions
- Reference specific files and line numbers from the context when relevant
- Maintain consistency with the project's tech stack and dependencies

Context Format:
You will receive relevant code snippets from the user's project with file paths and line numbers.
Use this context to inform your responses.
"""

def build_rag_prompt(
    system_prompt: str,
    context: str,
    query: str,
    conversation_history: List[Dict]
) -> str:
    """
    Build the complete prompt for RAG mode.
    """
    history_text = ""
    for msg in conversation_history[-5:]:  # Last 5 messages
        role = "User" if msg['role'] == 'user' else "Assistant"
        history_text += f"{role}: {msg['content']}\n\n"
    
    return f"""
{system_prompt}

===== RELEVANT CODE FROM PROJECT =====
{context}
======================================

===== CONVERSATION HISTORY =====
{history_text}
=================================

Current Question:
User: {query}

Instructions: Answer based on the provided code context. If generating code, match the existing patterns and style. Be specific and reference the relevant files when appropriate.
"""
