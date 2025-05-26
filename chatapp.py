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

# --- CSS STYLES OMITTED FOR BREVITY (keep your existing CSS block here) ---

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

# --- Chat Header ---
st.markdown("""
<div class="chat-container">
    <div class="chat-header">
        <h1>🤖 AI Chat Assistant</h1>
        <p>Your friendly AI companion for conversations</p>
    </div>
</div>
""", unsafe_allow_html=True)

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

    # Poll result until it’s ready
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

# --- Footer ---
st.markdown("""
<div style="text-align: center; padding: 2rem; color: white; opacity: 0.7;">
    <p style="color:black">✨ Developed By Karthikeyan S.P ✨</p>
    <p style="font-size: 0.8em;">Built with Streamlit • Powered by AI</p>
</div>
""", unsafe_allow_html=True)
