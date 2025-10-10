import streamlit as st
from typing import Tuple, Dict

def render_sidebar(api_client) -> Tuple[str, Dict]:
    """
    Render sidebar with mode selector and upload interface
    Returns: (mode, upload_status)
    """
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        
        # Unified chat mode (always uses RAG + LLM)
        st.markdown("### 🤖 AI Assistant")
        st.info("Powered by RAG + LLM - Ask about your project or anything else!")
        
        # Backend health check
        health = api_client.health_check()
        if health.get('status') == 'healthy':
            st.success("✓ Backend connected")
        else:
            st.error(f"❌ Backend error: {health.get('error', 'Unknown')}")
        
        # Always return unified mode
        st.session_state['mode'] = 'unified'
        return 'unified', {}

def render_conversation_controls():
    """
    Render conversation control buttons in sidebar
    """
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🔧 Conversation Controls")
        
        # Clear conversation button
        if st.session_state.get('messages'):
            if st.button("🗑️ Clear Conversation", use_container_width=True):
                st.session_state['messages'] = []
                st.success("Conversation cleared!")
                st.rerun()
        
        # Session info
        if st.session_state.get('session_id'):
            st.caption(f"Session: {st.session_state['session_id'][:8]}...")
        
        # Message count
        message_count = len(st.session_state.get('messages', []))
        st.caption(f"Messages: {message_count}")
        
        # Current mode
        st.caption("Mode: Unified RAG + LLM")
