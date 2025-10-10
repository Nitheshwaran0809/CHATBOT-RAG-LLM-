# Frontend Architecture Documentation

## 🎨 Streamlit Frontend Structure

### Main Application (`app.py`)
```python
# Streamlit app configuration
st.set_page_config(
    page_title="Code Assistant AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Key features:
- Custom CSS styling (ChatGPT dark theme)
- Session state management
- API client initialization
- Main layout structure
```

### Components Architecture

#### 1. Sidebar Component (`components/sidebar.py`)
```python
def render_sidebar(api_client) -> Tuple[str, Dict]:
    # Features:
    - Chat mode selector (General/Code Assistant)
    - Backend health check display
    - Clean, minimal interface
    - Session state management
```

**UI Elements:**
- Mode radio buttons (General Chat / Code Assistant)
- Backend connection status
- Conversation controls

#### 2. Chat Interface (`components/chat_interface.py`)
```python
def render_chat_interface(api_client, mode, upload_status):
    # Features:
    - Message history display
    - Streaming response handling
    - Input form with send button
    - Welcome messages for each mode
```

**Key Functions:**
- `render_message()` - Individual message bubbles
- `render_welcome_message()` - Mode-specific welcome screens
- Streaming response display
- Error handling and user feedback

### Services Layer

#### API Client (`services/api_client.py`)
```python
class APIClient:
    def __init__(self, backend_url: str):
        self.backend_url = backend_url
        self.session = requests.Session()
    
    # Methods:
    - chat_general() - General chat API calls
    - chat_code_assistant() - RAG-enhanced chat
    - get_code_assistant_status() - System status
    - clear_code_assistant() - Clear knowledge base
    - health_check() - Backend health
```

**Features:**
- Streaming response handling
- Session management
- Error handling and retries
- JSON response parsing

### Session State Management (`utils/session_state.py`)
```python
def initialize_session_state():
    # Session variables:
    - messages: List[Dict] - Chat history
    - session_id: str - Unique session identifier
    - mode: str - Current chat mode (general/code_assistant)
```

### Styling (`styles/chatgpt_theme.css`)
```css
/* ChatGPT-inspired dark theme */
- Dark background colors
- Message bubble styling
- Responsive design
- Modern UI elements
- Smooth animations
```

**Key Style Classes:**
- `.message-container` - Message wrapper
- `.user-bubble` - User message styling
- `.assistant-bubble` - AI response styling
- `.header` - App header styling

### UI Flow

#### 1. Application Startup
1. Load custom CSS
2. Initialize session state
3. Create API client
4. Render main layout

#### 2. Chat Flow
1. User selects mode (sidebar)
2. User types message
3. Message sent to appropriate API endpoint
4. Streaming response displayed
5. Message added to history
6. UI updates automatically

#### 3. Mode Switching
- **General Chat**: Direct LLM communication
- **Code Assistant**: RAG-enhanced responses with project context

### Key Features

#### Streaming Responses
```python
# Real-time token streaming
for token in response_generator:
    full_response += token
    response_placeholder.markdown(f"🤖 **Assistant**: {full_response}")
    time.sleep(0.01)  # Smooth streaming effect
```

#### Error Handling
- Connection error display
- API timeout handling
- User-friendly error messages
- Graceful degradation

#### Responsive Design
- Wide layout for better chat experience
- Mobile-friendly interface
- Proper column layouts
- Scrollable message history

### Configuration

#### Environment Variables
```python
backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
```

#### Page Configuration
- Wide layout mode
- Custom page title and icon
- Expanded sidebar by default
- Dark theme styling

### User Experience Features

#### Welcome Messages
- Mode-specific instructions
- Feature explanations
- Usage examples
- Clear call-to-actions

#### Message Display
- Timestamp support
- Role-based styling (user/assistant)
- Content formatting
- Responsive bubbles

#### Conversation Controls
- Clear conversation button
- Session information display
- Message count tracking
- Mode indicator

### Performance Optimizations
- Efficient state management
- Minimal re-renders
- Streaming for better UX
- Cached API client
- Optimized CSS loading

### Accessibility
- Semantic HTML structure
- Keyboard navigation support
- Screen reader friendly
- High contrast colors
- Clear visual hierarchy
