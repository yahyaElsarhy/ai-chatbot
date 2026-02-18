import streamlit as st
import httpx
import asyncio

# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Arduino Chatbot 🤖",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────
BACKEND_URL = "http://localhost:8000"

PROVIDERS = {
    "groq": {
    "label": "⚡ Groq (Fast & Free)",
    "models": [
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
        "gemma2-9b-it",
        "mixtral-8x7b-32768",
    ]
},
    "openrouter": {
        "label": "🌐 OpenRouter (Free Models)",
        "models": [
            "mistralai/mistral-7b-instruct:free",
            "meta-llama/llama-3-8b-instruct:free",
            "meta-llama/llama-3.1-8b-instruct:free",
            "google/gemma-2-9b-it:free",
            "microsoft/phi-3-mini-128k-instruct:free",
        ]
    },
  
}

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Main header */
    .main-header {
        text-align: center;
        padding: 1rem 0 0.5rem 0;
    }
    .main-header h1 {
        font-size: 2.2rem;
        font-weight: 800;
        color: #00C7BE;
    }
    .main-header p {
        color: #888;
        font-size: 0.95rem;
    }

    /* Chat bubbles */
    .chat-user {
        background: #1e3a5f;
        color: white;
        padding: 0.8rem 1.1rem;
        border-radius: 18px 18px 4px 18px;
        margin: 0.4rem 0;
        max-width: 80%;
        margin-left: auto;
        font-size: 0.95rem;
    }
    .chat-assistant {
        background: #1e1e2e;
        color: #e0e0e0;
        padding: 0.8rem 1.1rem;
        border-radius: 18px 18px 18px 4px;
        margin: 0.4rem 0;
        max-width: 85%;
        font-size: 0.95rem;
        border-left: 3px solid #00C7BE;
    }

    /* Provider badge */
    .provider-badge {
        display: inline-block;
        background: #00C7BE22;
        color: #00C7BE;
        border: 1px solid #00C7BE55;
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.75rem;
        margin-bottom: 0.5rem;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #0d1117;
    }

    /* Input area */
    .stTextArea textarea {
        border-radius: 12px;
        border: 1px solid #333;
        background: #1e1e2e;
        color: white;
    }

    /* Send button */
    div[data-testid="stButton"] button {
        background: #00C7BE;
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        width: 100%;
        padding: 0.6rem;
        font-size: 1rem;
    }
    div[data-testid="stButton"] button:hover {
        background: #00a89f;
    }

    /* Hide streamlit default elements */
    #MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Session State Init
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "provider" not in st.session_state:
    st.session_state.provider = "groq"

if "model" not in st.session_state:
    st.session_state.model = PROVIDERS["groq"]["models"][0]


# ─────────────────────────────────────────────
# Helper: Send message to Backend
# ─────────────────────────────────────────────
def send_message(message: str, provider: str, model: str, history: list) -> dict:
    """Send message to FastAPI backend and return response"""
    try:
        response = httpx.post(
            f"{BACKEND_URL}/chat",
            json={
                "message": message,
                "provider": provider,
                "model": model,
                "conversation_history": history
            },
            timeout=60.0
        )
        response.raise_for_status()
        return {"success": True, "data": response.json()}

    except httpx.ConnectError:
        return {
            "success": False,
            "error": "❌ Cannot connect to backend!\nMake sure FastAPI is running:\n`uvicorn backend.main:app --reload`"
        }
    except httpx.TimeoutException:
        return {"success": False, "error": "⏱️ Request timeout. Try again or switch provider."}
    except httpx.HTTPStatusError as e:
        return {"success": False, "error": f"❌ Backend error {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def check_backend_health() -> dict:
    """Check if backend is running and which providers are ready"""
    try:
        response = httpx.get(f"{BACKEND_URL}/health", timeout=5.0)
        return {"online": True, "data": response.json()}
    except Exception:
        return {"online": False}


# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.divider()

    # Backend status
    health = check_backend_health()
    if health["online"]:
        st.success("🟢 Backend Online")
        providers_status = health.get("data", {}).get("providers", {})
        for prov, ready in providers_status.items():
            icon = "✅" if ready else "❌"
            st.caption(f"{icon} {prov.capitalize()}")
    else:
        st.error("🔴 Backend Offline")
        st.caption("Run: `uvicorn backend.main:app --reload`")

    st.divider()

    # Provider selector
    st.markdown("### 🤖 AI Provider")
    provider_key = st.selectbox(
        "Choose provider",
        options=list(PROVIDERS.keys()),
        format_func=lambda x: PROVIDERS[x]["label"],
        key="provider_select",
        label_visibility="collapsed"
    )
    st.session_state.provider = provider_key

    # Model selector
    st.markdown("### 🧠 Model")
    available_models = PROVIDERS[provider_key]["models"]
    selected_model = st.selectbox(
        "Choose model",
        options=available_models,
        key="model_select",
        label_visibility="collapsed"
    )
    st.session_state.model = selected_model

    st.divider()

    # Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    # Info box
    st.markdown("### 💡 Quick Tips")
    st.info(
        "Ask me about:\n"
        "- Arduino basics\n"
        "- Sensors & motors\n"
        "- Code debugging\n"
        "- Circuit wiring\n"
        "- Project ideas"
    )

    st.caption("Built for International School Students 🎓")


# ─────────────────────────────────────────────
# Main Header
# ─────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🤖 Arduino Chatbot</h1>
    <p>Your AI assistant for learning Arduino — Ask anything!</p>
</div>
""", unsafe_allow_html=True)

st.divider()


# ─────────────────────────────────────────────
# Chat History Display
# ─────────────────────────────────────────────
chat_container = st.container()

with chat_container:
    if not st.session_state.messages:
        st.markdown("""
        <div style='text-align:center; color:#555; padding: 2rem 0;'>
            <div style='font-size:3rem;'>⚡</div>
            <div style='font-size:1.1rem; margin-top:0.5rem;'>Ask your first Arduino question!</div>
            <div style='font-size:0.85rem; color:#444; margin-top:0.3rem;'>
                e.g. "How do I blink an LED?" or "What is a servo motor?"
            </div>
        </div>
        """, unsafe_allow_html=True)

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="chat-user">👤 {msg['content']}</div>
            """, unsafe_allow_html=True)
        else:
            provider_used = msg.get("provider", "")
            model_used = msg.get("model", "")
            st.markdown(f"""
            <div class="chat-assistant">
                <span class="provider-badge">🤖 {provider_used} · {model_used}</span><br>
                {msg['content']}
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Input Area
# ─────────────────────────────────────────────
st.divider()

with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_area(
        "Your question:",
        placeholder="e.g. How do I connect a DHT11 sensor to Arduino?",
        height=80,
        label_visibility="collapsed"
    )
    submitted = st.form_submit_button("Send ➤", use_container_width=True)

if submitted and user_input.strip():
    # Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": user_input.strip()
    })

    # Build history for API (exclude provider/model metadata)
    api_history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[:-1]  # Exclude current message
    ]

    # Show spinner while waiting
    with st.spinner(f"🤖 Thinking with {st.session_state.provider}..."):
        result = send_message(
            message=user_input.strip(),
            provider=st.session_state.provider,
            model=st.session_state.model,
            history=api_history
        )

    if result["success"]:
        data = result["data"]
        st.session_state.messages.append({
            "role": "assistant",
            "content": data["response"],
            "provider": data["provider"],
            "model": data["model"]
        })
    else:
        st.error(result["error"])

    st.rerun()