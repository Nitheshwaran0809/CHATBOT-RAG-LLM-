import streamlit as st
import uuid

def initialize_session_state():
    """
    Initialize Streamlit session state variables
    """
    # Session ID for backend communication
    if 'session_id' not in st.session_state:
        st.session_state['session_id'] = str(uuid.uuid4())
    
    # Chat mode (unified RAG + LLM)
    if 'mode' not in st.session_state:
        st.session_state['mode'] = 'unified'
    
    # Message history
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []
    
    # Upload status for code assistant
    if 'upload_status' not in st.session_state:
        st.session_state['upload_status'] = {
            'is_ready': False,
            'documents_count': 0,
            'chunks_count': 0
        }
    
    # Current input
    if 'current_input' not in st.session_state:
        st.session_state['current_input'] = ""
    
    # Loading state
    if 'is_loading' not in st.session_state:
        st.session_state['is_loading'] = False
