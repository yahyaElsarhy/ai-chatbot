import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()


# ─────────────────────────────────────────────
# API Keys
# ─────────────────────────────────────────────
GROQ_API_KEY         = os.getenv("GROQ_API_KEY", "")
OPENROUTER_API_KEY   = os.getenv("OPENROUTER_API_KEY", "")



# ─────────────────────────────────────────────
# Provider Settings
# ─────────────────────────────────────────────
DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "groq")   # groq | openrouter | ollama | anthropic

PROVIDER_MODELS = {
    "groq": os.getenv("GROQ_MODEL", "llama3-8b-8192"),
    "openrouter": os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct:free"),
    "ollama": os.getenv("OLLAMA_MODEL", "llama3"),
    
}


# ─────────────────────────────────────────────
# Ollama Settings (Local)
# ─────────────────────────────────────────────
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


# ─────────────────────────────────────────────
# App Settings
# ─────────────────────────────────────────────
APP_TITLE       = "Arduino Chatbot 🤖"
APP_DESCRIPTION = "AI Assistant for Arduino — Powered by Free AI Models"
APP_VERSION     = "1.0.0"

SITE_URL        = os.getenv("SITE_URL", "http://localhost:8000")
SITE_NAME       = os.getenv("SITE_NAME", "Arduino Chatbot")


# ─────────────────────────────────────────────
# Chat Settings
# ─────────────────────────────────────────────
MAX_HISTORY_MESSAGES = 10    # Max messages to keep in conversation memory
MAX_TOKENS           = 1024  # Max tokens per response
TEMPERATURE          = 0.7   # Creativity level (0 = focused, 1 = creative)


# ─────────────────────────────────────────────
# Arduino System Prompt
# ─────────────────────────────────────────────
SYSTEM_PROMPT = """
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
# Validation — check which providers are ready
# ─────────────────────────────────────────────
def get_available_providers() -> dict:
    """Returns which providers are configured and ready to use"""
    return {
        "groq":        {"ready": bool(GROQ_API_KEY),       "free": True},
        "openrouter":  {"ready": bool(OPENROUTER_API_KEY), "free": True},
        "ollama":      {"ready": True,                     "free": True},   # Always available
        "anthropic":   {"ready": bool(ANTHROPIC_API_KEY),  "free": False},  # Paid
    }


def get_default_model(provider: str) -> str:
    """Returns the default model for a given provider"""
    return PROVIDER_MODELS.get(provider, "")


def validate_config():
    """
    Validates configuration on startup.
    Warns if no providers are configured.
    """
    providers = get_available_providers()
    ready = [name for name, info in providers.items() if info["ready"]]

    if not ready:
        print("⚠️  WARNING: No AI providers configured!")
        print("   Add at least one API key to your .env file:")
        print("   GROQ_API_KEY=...        (free) → https://console.groq.com/keys")
        print("   OPENROUTER_API_KEY=...  (free) → https://openrouter.ai/keys")
        print("   Or install Ollama locally → https://ollama.com")
    else:
        print(f"✅ Ready providers: {', '.join(ready)}")
        print(f"🎯 Default provider: {DEFAULT_PROVIDER}")

    return ready


# ─────────────────────────────────────────────
# Run validation on import
# ─────────────────────────────────────────────
if __name__ == "__main__":
    validate_config()