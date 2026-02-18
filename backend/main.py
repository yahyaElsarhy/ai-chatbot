from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Arduino Chatbot API 🤖",
    description="AI Chatbot for teaching Arduino to students",
    version="1.0.0"
)

# ─────────────────────────────────────────────
# CORS Middleware (allows Streamlit to connect)
# ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# Request / Response Models
# ─────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    provider: str = "groq"          # groq | openrouter
    model: Optional[str] = None     # optional: override default model
    conversation_history: list = [] # list of {"role": "user/assistant", "content": "..."}

class ChatResponse(BaseModel):
    response: str
    provider: str
    model: str

# ─────────────────────────────────────────────
# Arduino System Prompt
# ─────────────────────────────────────────────
ARDUINO_SYSTEM_PROMPT = """
You are an expert Arduino teaching assistant designed for international school students.
Your role is to:
- Explain Arduino concepts in simple, clear language
- Help students with Arduino code, circuits, and projects
- Answer questions about sensors, actuators, motors, LEDs, and other components
- Debug Arduino code and explain errors
- Suggest beginner-friendly projects
- Use examples and analogies to make learning fun

Always:
- Be encouraging and patient
- Break complex topics into simple steps
- Provide working code examples when asked
- Explain what each line of code does
- Suggest safety precautions when relevant

You ONLY answer questions related to Arduino, electronics, and programming.
If asked about unrelated topics, politely redirect the student to Arduino topics.
"""

# ─────────────────────────────────────────────
# Provider Router
# ─────────────────────────────────────────────
def get_provider(provider_name: str):
    """Return the correct provider based on name"""
    provider_name = provider_name.lower()

    if provider_name == "groq":
        from providers.groq_provider import GroqProvider
        return GroqProvider()

    elif provider_name == "openrouter":
        from providers.openrouter_provider import OpenRouterProvider
        return OpenRouterProvider()

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown provider: '{provider_name}'. Use: groq | openrouter"
        )

# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────
@app.get("/")
def read_root():
    return {
        "message": "Arduino Chatbot API is running! 🚀",
        "docs": "/docs",
        "available_providers": ["groq", "openrouter"]
    }


@app.get("/health")
def health_check():
    """Check which providers are configured"""
    return {
        "status": "ok",
        "providers": {
            "groq":       bool(os.getenv("GROQ_API_KEY")),
            "openrouter": bool(os.getenv("OPENROUTER_API_KEY")),
        }
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint.
    Sends message to selected AI provider and returns Arduino-focused response.
    """
    try:
        # Get the selected provider
        provider = get_provider(request.provider)

        # Build conversation with system prompt
        messages = [{"role": "system", "content": ARDUINO_SYSTEM_PROMPT}]

        # Add conversation history (last 10 messages to avoid token overflow)
        history = request.conversation_history[-10:]
        messages.extend(history)

        # Add current user message
        messages.append({"role": "user", "content": request.message})

        # Get response from provider
        result = await provider.chat(
            messages=messages,
            model=request.model
        )

        return ChatResponse(
            response=result["response"],
            provider=request.provider,
            model=result["model"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/providers")
def list_providers():
    """List all available providers and their default models"""
    return {
        "providers": [
            {
                "name": "groq",
                "description": "Fast & free - Best for students ⚡",
                "default_model": "llama3-8b-8192",
                "requires_api_key": True
            },
            {
                "name": "openrouter",
                "description": "Multiple free models available 🌐",
                "default_model": "mistralai/mistral-7b-instruct:free",
                "requires_api_key": True
            }
        ]
    }