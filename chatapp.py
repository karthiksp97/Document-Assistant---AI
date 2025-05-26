import streamlit as st
import random
import time
from datetime import datetime
import threading
import queue

from retrive import runtheretrive

# Configure page
st.set_page_config(
    page_title="AI Chat Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS with stunning developer banner
st.markdown("""
<style>
/* Stunning Developer Banner Styles */
.developer-banner {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1rem 2rem;
    border-radius: 15px;
    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    animation: glow 2s ease-in-out infinite alternate;
}

.developer-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
    animation: shine 3s infinite;
}

@keyframes glow {
    from { box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3); }
    to { box-shadow: 0 15px 40px rgba(102, 126, 234, 0.6); }
}

@keyframes shine {
    0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
    100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
}

.developer-content {
    position: relative;
    z-index: 2;
    text-align: center;
    color: white;
}

.developer-title {
    font-size: 2.5rem;
    font-weight: bold;
    margin: 0;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    animation: bounce 2s infinite;
}

@keyframes bounce {
    0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
    40% { transform: translateY(-10px); }
    60% { transform: translateY(-5px); }
}

.developer-subtitle {
    font-size: 1.2rem;
    margin: 0.5rem 0;
    opacity: 0.9;
    font-style: italic;
}

.developer-badges {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-top: 1rem;
    flex-wrap: wrap;
}

.badge {
    background: rgba(255,255,255,0.2);
    padding: 0.5rem 1rem;
    border-radius: 25px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.3);
    font-size: 0.9rem;
    transition: all 0.3s ease;
}

.badge:hover {
    background: rgba(255,255,255,0.3);
    transform: translateY(-2px);
}

/* Floating particles */
.particles {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    z-index: 1;
}

.particle {
    position: absolute;
    background: rgba(255,255,255,0.5);
    border-radius: 50%;
    animation: float 6s infinite ease-in-out;
}

.particle:nth-child(1) { width: 6px; height: 6px; left: 10%; animation-delay: 0s; }
.particle:nth-child(2) { width: 8px; height: 8px; left: 20%; animation-delay: 1s; }
.particle:nth-child(3) { width: 4px; height: 4px; left: 30%; animation-delay: 2s; }
.particle:nth-child(4) { width: 10px; height: 10px; left: 70%; animation-delay: 1.5s; }
.particle:nth-child(5) { width: 5px; height: 5px; left: 80%; animation-delay: 3s; }

@keyframes float {
    0%, 100% { transform: translateY(100px) rotate(0deg); opacity: 0; }
    50% { transform: translateY(-20px) rotate(180deg); opacity: 1; }
}

/* Chat container styles */
.chat-container {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    border-radius: 20px;
    padding: 2rem;
    margin: 1rem 0;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}

.chat-header {
    text-align: center;
    margin-bottom: 2rem;
}

.chat-header h1 {
    background: linear-gradient(45deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 2.5rem;
    margin: 0;
}

/* Message styles */
.user-message {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 1rem;
    border-radius: 18px;
    margin: 0.5rem 0;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.assistant-message {
    background: linear-gradient(135deg, #f093fb, #f5576c);
    color: white;
    padding: 1rem;
    border-radius: 18px;
    margin: 0.5rem 0;
    box-shadow: 0 4px 15px rgba(245, 87, 108, 0.3);
}

.timestamp {
    font-size: 0.8em;
    opacity: 0.8;
    margin-top: 0.5rem;
}

/* Typing indicator */
.typing-indicator {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 1rem;
    background: linear-gradient(135deg, #a8edea, #fed6e3);
    border-radius: 18px;
    color: #333;
}

.typing-dots {
    display: flex;
    gap: 4px;
}

.typing-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #667eea;
    animation: typing 1.4s infinite ease-in-out;
}

.typing-dot:nth-child(1) { animation-delay: -0.32s; }
.typing-dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
    0%, 80%, 100% { transform: scale(0); opacity: 0.5; }
    40% { transform: scale(1); opacity: 1; }
}

/* Sidebar styles */
.sidebar-content {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
}

</style>
""", unsafe_allow_html=True)

# STUNNING DEVELOPER BANNER - First thing everyone sees!
st.markdown("""
<div class="developer-banner">
    <div class="particles">
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
    </div>
    <div class="developer-content">
        <h1 class="developer-title">✨ DEVELOPED BY KARTHIKEYAN S.P ✨</h1>
        <p class="developer-subtitle">🚀 AI Innovation Specialist | Full-Stack Developer | Tech Visionary</p>
        <div class="developer-badges">
            <span class="badge">🤖 AI Expert</span>
            <span class="badge">💻 Python Developer</span>
            <span class="badge">🎨Gen AI</span>
            <span class="badge">⚡ Innovation Leader</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Enhanced CSS for readable UI
st.markdown("""
<style>
/* Chat container styles */
.chat-container {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    border-radius: 20px;
    padding: 2rem;
    margin: 1rem 0;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}

.chat-header {
    text-align: center;
    margin-bottom: 2rem;
}

.chat-header h1 {
    background: linear-gradient(45deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 2.5rem;
    margin: 0;
}

.chat-header p {
    font-size: 1.2rem;
    color: #666;
}

/* Message styles */
.user-message {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 1rem;
    border-radius: 18px;
    margin: 0.5rem 0;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.assistant-message {
    background: linear-gradient(135deg, #f093fb, #f5576c);
    color: white;
    padding: 1rem;
    border-radius: 18px;
    margin: 0.5rem 0;
    box-shadow: 0 4px 15px rgba(245, 87, 108, 0.3);
}

.timestamp {
    font-size: 0.8em;
    opacity: 0.8;
    margin-top: 0.5rem;
}

/* Typing indicator */
.typing-indicator {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 1rem;
    background: linear-gradient(135deg, #a8edea, #fed6e3);
    border-radius: 18px;
    color: #333;
}

.typing-dots {
    display: flex;
    gap: 4px;
}

.typing-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #667eea;
    animation: typing 1.4s infinite ease-in-out;
}

.typing-dot:nth-child(1) { animation-delay: -0.32s; }
.typing-dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
    0%, 80%, 100% { transform: scale(0); opacity: 0.5; }
    40% { transform: scale(1); opacity: 1; }
}

/* Sidebar styles */
.sidebar-content {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# --- Chat Header ---
st.markdown("""
<div class="chat-container">
    <div class="chat-header">
        <h1>🤖 AI Chat Assistant</h1>
        <p>Your friendly AI companion for conversations</p>
    </div>
</div>
""", unsafe_allow_html=True)



# --- Sidebar ---
with st.sidebar:
    st.markdown("### 🤖 Chat Assistant")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_started" not in st.session_state:
        st.session_state.chat_started = datetime.now()

    message_count = len(st.session_state.messages)
    user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
    assistant_messages = len([m for m in st.session_state.messages if m["role"] == "assistant"])

    st.markdown(f"""
    <div class="sidebar-content">
        <h4>📊 Chat Stats</h4>
        <p>💬 Total Messages: {message_count}</p>
        <p>👤 Your Messages: {user_messages}</p>
        <p>🤖 AI Messages: {assistant_messages}</p>
        <p>⏰ Session Started: {st.session_state.chat_started.strftime('%H:%M')}</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🗑️ Clear Chat", type="secondary", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_started = datetime.now()
        st.rerun()

    st.markdown("### 🎨 Personalization")
    chat_theme = st.selectbox("Choose Theme:", ["Default", "Dark Mode", "Ocean", "Sunset"], index=0)
    response_speed = st.slider("Response Speed", 0.01, 0.2, 0.05, 0.01, help="Adjust how fast the AI types")

# --- Display previous messages ---
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
        st.markdown(f"""
        <div class="{ 'user-message' if message['role'] == 'user' else 'assistant-message' }">
            {message['content']}
            <div class="timestamp">
                {message.get('timestamp', datetime.now().strftime('%H:%M:%S'))}
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- Chat Input ---
col1, col2 = st.columns([6, 1])
with col1:
    prompt = st.chat_input("💭 What's on your mind? Type your message here...", key="chat_input")

with col2:
    if st.button("🎲", help="Get a random conversation starter", type="secondary"):
        starters = [
            "Tell me a fun fact!",
            "What's the weather like?",
            "Can you help me brainstorm ideas?",
            "What's new in technology?",
            "Tell me a joke!",
            "How are you doing today?"
        ]
        prompt = random.choice(starters)
st.markdown("""
<div style="text-align: center; margin: 2rem 0; padding: 1rem; background: linear-gradient(45deg, #f093fb, #f5576c); border-radius: 15px; color: white;">
    <h3 style="margin: 0;">🎯 Built with Passion by Karthikeyan S.P</h3>
    <p style="margin: 0.5rem 0; opacity: 0.9;">Crafting the Future of AI Conversations</p>
</div>
""", unsafe_allow_html=True)
# --- Process Prompt ---
if prompt:
    current_time = datetime.now().strftime('%H:%M:%S')

    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "timestamp": current_time
    })

    with st.chat_message("user", avatar="👤"):
        st.markdown(f"""
        <div class="user-message">
            {prompt}
            <div class="timestamp">{current_time}</div>
        </div>
        """, unsafe_allow_html=True)

    # Placeholder for assistant message
    typing_placeholder = st.empty()

    # Thread-safe queue to fetch result
    result_queue = queue.Queue()

    def fetch_response():
        response = runtheretrive(prompt)
        result_queue.put(response)

    # Start background thread
    thread = threading.Thread(target=fetch_response)
    thread.start()

    with typing_placeholder:
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown("""
            <div class="typing-indicator">
                <span>🤖 AI is thinking</span>
                <div class="typing-dots">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Poll result until it's ready
    while thread.is_alive():
        time.sleep(0.2)

    # Get response from queue
    response_text = result_queue.get()
    typing_placeholder.empty()

    # Display assistant response with typing effect
    with st.chat_message("assistant", avatar="🤖"):
        def dynamic_response_generator():
            for word in response_text.split():
                yield word + " "
                time.sleep(response_speed)

        response = st.write_stream(dynamic_response_generator())
        response_time = datetime.now().strftime('%H:%M:%S')

        st.markdown(f"""
        <div class="timestamp" style="text-align: right; color: #666; font-size: 0.8em;">
            {response_time}
        </div>
        """, unsafe_allow_html=True)

    # Save assistant message
    st.session_state.messages.append({
        "role": "assistant",
        "content": response_text,
        "timestamp": response_time
    })

    

    # Force re-render to ensure UI updates with the new message
    st.rerun()

