import streamlit as st
from datetime import datetime
import time

def render_message(role: str, content: str, timestamp: str = None):
    """
    Render a single message bubble with styling
    """
    is_user = role == 'user'
    
    # CSS classes and icon
    bubble_class = "user-bubble" if is_user else "assistant-bubble"
    icon = "👤" if is_user else "🤖"
    
    # Format timestamp
    time_str = ""
    if timestamp:
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime("%I:%M %p")
        except:
            time_str = ""
    
    # Render message
    with st.container():
        col1, col2, col3 = st.columns([1, 8, 1])
        
        if is_user:
            # User message (right-aligned)
            with col2:
                st.markdown(
                    f"""
                    <div class="message-container {bubble_class}">
                        <div class="message-content">
                            <div class="message-text">{content}</div>
                            {f'<div class="message-timestamp">{time_str}</div>' if time_str else ''}
                        </div>
                        <div class="message-icon">{icon}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            # Assistant message (left-aligned)
            with col2:
                st.markdown(
                    f"""
                    <div class="message-container {bubble_class}">
                        <div class="message-icon">{icon}</div>
                        <div class="message-content">
                            <div class="message-text">{content}</div>
                            {f'<div class="message-timestamp">{time_str}</div>' if time_str else ''}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

def render_chat_interface(api_client, mode, upload_status):
    """
    Render main chat interface with message history and input
    """
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        # Render message history
        for message in st.session_state.get('messages', []):
            render_message(
                role=message['role'],
                content=message['content'],
                timestamp=message.get('timestamp')
            )
    
    # Input area
    st.markdown("---")
    
    # Input is always enabled for unified mode
    input_disabled = False
    placeholder_text = "Ask me anything about your project or general questions..."
    
    # Input form
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([9, 1])
        
        with col1:
            user_input = st.text_area(
                "Message",
                placeholder=placeholder_text,
                disabled=input_disabled,
                label_visibility="collapsed",
                height=100,
                key="user_input_area"
            )
        
        with col2:
            send_button = st.form_submit_button(
                "🚀 Send", 
                use_container_width=True,
                disabled=input_disabled
            )
    
    # Handle message sending
    if send_button and user_input.strip():
        # Add user message to history
        user_message = {
            'role': 'user',
            'content': user_input.strip(),
            'timestamp': datetime.now().isoformat()
        }
        st.session_state['messages'].append(user_message)
        
        # Show typing indicator
        with st.spinner("🤖 Assistant is thinking..."):
            # Create placeholder for streaming response
            response_placeholder = st.empty()
            
            try:
                # Always use RAG-enhanced chat (unified mode)
                conversation_history = [
                    {"role": msg["role"], "content": msg["content"]} 
                    for msg in st.session_state['messages'][:-1]  # Exclude current message
                ]
                response_generator = api_client.chat_code_assistant(
                    message=user_input.strip(),
                    session_id=st.session_state.get('session_id'),
                    conversation_history=conversation_history
                )
                
                # Stream the response
                full_response = ""
                for token in response_generator:
                    full_response += token
                    # Update the placeholder with accumulated response
                    response_placeholder.markdown(f"🤖 **Assistant**: {full_response}")
                    time.sleep(0.01)  # Small delay for smooth streaming effect
                
                # Add assistant response to history
                assistant_message = {
                    'role': 'assistant',
                    'content': full_response,
                    'timestamp': datetime.now().isoformat()
                }
                st.session_state['messages'].append(assistant_message)
                
                # Clear the placeholder and rerun to show final messages
                response_placeholder.empty()
                st.rerun()
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                # Remove the user message if there was an error
                if st.session_state['messages'] and st.session_state['messages'][-1] == user_message:
                    st.session_state['messages'].pop()

def render_welcome_message():
    """
    Render welcome message when no conversation exists
    """
    if not st.session_state.get('messages'):
        st.markdown(
            """
            <div style="text-align: center; padding: 2rem; color: #8E8EA0;">
                <h2>🤖 AI Assistant</h2>
                <p>Unified RAG + LLM powered by your project knowledge</p>
                <br>
                <div style="text-align: left; max-width: 600px; margin: 0 auto;">
                    <h3>🎯 Ask me anything:</h3>
                    <ul>
                        <li><strong>Project Questions:</strong> "How is this project structured?"</li>
                        <li><strong>Code Generation:</strong> "Create a new API endpoint"</li>
                        <li><strong>Debugging:</strong> "Fix this error in my code"</li>
                        <li><strong>Architecture:</strong> "How do I improve performance?"</li>
                        <li><strong>General Programming:</strong> "Explain async/await in Python"</li>
                        <li><strong>Deployment:</strong> "How do I deploy this application?"</li>
                    </ul>
                    <br>
                    <h3>✨ Intelligent Features:</h3>
                    <ul>
                        <li>🧠 <strong>Smart Context:</strong> Automatically uses your project docs when relevant</li>
                        <li>🔍 <strong>RAG Search:</strong> Finds relevant information from 408 knowledge chunks</li>
                        <li>💡 <strong>Fallback LLM:</strong> Answers general questions when no project context needed</li>
                        <li>🎯 <strong>Unified Experience:</strong> One chat for everything - no mode switching!</li>
                    </ul>
                </div>
                <br>
                <p style="font-size: 0.9em; opacity: 0.8;">
                    💾 <strong>Knowledge Base:</strong> Loaded with your complete project documentation
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
