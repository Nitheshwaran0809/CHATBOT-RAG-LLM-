import streamlit as st
import os
from components.sidebar import render_sidebar, render_conversation_controls
from components.chat_interface import render_chat_interface, render_welcome_message
from services.api_client import APIClient
from utils.session_state import initialize_session_state

# Page config
st.set_page_config(
    page_title="Code Assistant AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
css_path = os.path.join(os.path.dirname(__file__), 'styles', 'chatgpt_theme.css')
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize session state
initialize_session_state()

# Initialize API client
backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
api_client = APIClient(backend_url=backend_url)

def main():
    """
    Main application function
    """
    # Header
    st.markdown(
        """
        <div class="header">
            <h1>🤖 AI Assistant</h1>
            <p style="margin: 0; color: rgba(255,255,255,0.8);">Unified RAG + LLM - One Chat for Everything</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Sidebar
    mode, upload_status = render_sidebar(api_client)
    render_conversation_controls()
    
    # Main content area
    col1, col2, col3 = st.columns([1, 10, 1])
    
    with col2:
        # Show welcome message if no conversation
        render_welcome_message()
        
        # Main chat interface
        render_chat_interface(api_client, mode, upload_status)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #8E8EA0; font-size: 0.8rem;">
            <p>🚀 <strong>AI Assistant v1.0.0</strong> | Powered by Groq & ChromaDB</p>
            <p>✅ <strong>UNIFIED EXPERIENCE</strong> | RAG + LLM in One Chat</p>
            <p>🧠 Smart Context • 🔍 408 Knowledge Chunks • 💡 Intelligent Responses</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
