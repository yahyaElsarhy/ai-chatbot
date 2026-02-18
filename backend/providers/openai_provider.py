import os
import httpx
from typing import Optional


class OpenRouterProvider:
    """
    OpenRouter AI Provider 🌐
    Access 50+ models (many FREE) through one API
    Docs: https://openrouter.ai/docs
    Free models list: https://openrouter.ai/models?q=free
    """

    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    # 100% Free models on OpenRouter (no credits needed)
    AVAILABLE_MODELS = {
        # ── Free Models ──────────────────────────────────────────
        "mistralai/mistral-7b-instruct:free":       "Mistral 7B — Fast & reliable ⚡ (FREE)",
        "meta-llama/llama-3-8b-instruct:free":      "Llama 3 8B — Great for students 🦙 (FREE)",
        "meta-llama/llama-3.1-8b-instruct:free":    "Llama 3.1 8B — Improved version 🦙 (FREE)",
        "google/gemma-2-9b-it:free":                "Gemma 2 9B — Google model 🔵 (FREE)",
        "microsoft/phi-3-mini-128k-instruct:free":  "Phi-3 Mini — Small but smart 🔬 (FREE)",
        "qwen/qwen-2-7b-instruct:free":             "Qwen 2 7B — Multilingual 🌍 (FREE)",
        # ── Paid Models (with free credits) ──────────────────────
        "mistralai/mixtral-8x7b-instruct":          "Mixtral 8x7B — Long context 📄 (Credits)",
        "openai/gpt-3.5-turbo":                     "GPT-3.5 Turbo — OpenAI 🟢 (Credits)",
    }

    DEFAULT_MODEL = "mistralai/mistral-7b-instruct:free"

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "❌ OPENROUTER_API_KEY not found!\n"
                "Get your free key from: https://openrouter.ai/keys\n"
                "Then add it to your .env file: OPENROUTER_API_KEY=your_key_here"
            )

        # Your site info (shown on OpenRouter dashboard)
        self.site_url = os.getenv("SITE_URL", "http://localhost:8000")
        self.site_name = os.getenv("SITE_NAME", "Arduino Chatbot")

    async def chat(self, messages: list, model: Optional[str] = None) -> dict:
        """
        Send messages to OpenRouter and return response.

        Args:
            messages: List of {"role": "...", "content": "..."} dicts
            model: Optional model override (uses DEFAULT_MODEL if None)

        Returns:
            dict with "response" and "model" keys
        """
        selected_model = model or self.DEFAULT_MODEL

        # Fallback to default if unknown model
        if selected_model not in self.AVAILABLE_MODELS:
            selected_model = self.DEFAULT_MODEL

        headers = {
            "Authorization":   f"Bearer {self.api_key}",
            "Content-Type":    "application/json",
            # OpenRouter recommends these headers
            "HTTP-Referer":    self.site_url,
            "X-Title":         self.site_name,
        }

        payload = {
            "model":       selected_model,
            "messages":    messages,
            "temperature": 0.7,
            "max_tokens":  1024,
            "top_p":       1,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:  # 60s (some free models are slower)
            try:
                response = await client.post(
                    self.BASE_URL,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()

            except httpx.TimeoutException:
                raise Exception(
                    "⏱️ OpenRouter timeout.\n"
                    "Free models can be slow sometimes. Try again or switch to Groq."
                )

            except httpx.HTTPStatusError as e:
                status = e.response.status_code

                if status == 401:
                    raise Exception("🔑 Invalid OPENROUTER_API_KEY. Check your .env file.")
                elif status == 402:
                    raise Exception(
                        "💳 No credits left on OpenRouter.\n"
                        "Switch to a free model (models ending in ':free') or add credits."
                    )
                elif status == 429:
                    raise Exception("🚦 OpenRouter rate limit reached. Wait a moment and try again.")
                elif status == 503:
                    raise Exception(
                        "🔧 OpenRouter model unavailable.\n"
                        "Try a different model or switch to Groq provider."
                    )
                else:
                    raise Exception(f"❌ OpenRouter API error {status}: {e.response.text}")

        data = response.json()

        # OpenRouter sometimes returns errors inside 200 responses
        if "error" in data:
            error_msg = data["error"].get("message", "Unknown error")
            raise Exception(f"❌ OpenRouter error: {error_msg}")

        return {
            "response": data["choices"][0]["message"]["content"],
            "model":    selected_model
        }

    @staticmethod
    def list_models() -> dict:
        """Return all available OpenRouter models"""
        return OpenRouterProvider.AVAILABLE_MODELS

    @staticmethod
    def list_free_models() -> dict:
        """Return only the FREE models"""
        return {
            k: v for k, v in OpenRouterProvider.AVAILABLE_MODELS.items()
            if ":free" in k
        }