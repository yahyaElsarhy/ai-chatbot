import os
import httpx
from typing import Optional

class GroqProvider:
    """
    Groq AI Provider - Fast & Free ⚡
    Docs: https://console.groq.com/docs
    """

    BASE_URL = "https://api.groq.com/openai/v1/chat/completions"

    # Available FREE models on Groq
    AVAILABLE_MODELS = {
    "llama-3.1-8b-instant":   "Llama 3.1 8B — Fast & Free ⚡",
    "llama-3.3-70b-versatile": "Llama 3.3 70B — Smarter 🧠",
    "gemma2-9b-it":            "Gemma 2 9B — Google model 🔵",
    "mixtral-8x7b-32768":      "Mixtral 8x7B — Long context 📄",
}

    DEFAULT_MODEL = "llama-3.1-8b-instant"

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError(
                "❌ GROQ_API_KEY not found!\n"
                "Get your free key from: https://console.groq.com/keys\n"
                "Then add it to your .env file: GROQ_API_KEY=your_key_here"
            )

    async def chat(self, messages: list, model: Optional[str] = None) -> dict:
        """
        Send messages to Groq and return response.

        Args:
            messages: List of {"role": "...", "content": "..."} dicts
            model: Optional model override (uses DEFAULT_MODEL if None)

        Returns:
            dict with "response" and "model" keys
        """
        selected_model = model or self.DEFAULT_MODEL

        # Validate model
        if selected_model not in self.AVAILABLE_MODELS:
            selected_model = self.DEFAULT_MODEL

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": selected_model,
            "messages": messages,
            "temperature": 0.7,        # Balanced creativity
            "max_tokens": 1024,        # Good for detailed Arduino explanations
            "top_p": 1,
            "stream": False
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    self.BASE_URL,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()

            except httpx.TimeoutException:
                raise Exception("⏱️ Groq API timeout. Please try again.")

            except httpx.HTTPStatusError as e:
                status = e.response.status_code

                if status == 401:
                    raise Exception("🔑 Invalid GROQ_API_KEY. Check your .env file.")
                elif status == 429:
                    raise Exception("🚦 Groq rate limit reached. Wait a moment and try again.")
                elif status == 503:
                    raise Exception("🔧 Groq service unavailable. Try another provider.")
                else:
                    raise Exception(f"❌ Groq API error {status}: {e.response.text}")

        data = response.json()

        return {
            "response": data["choices"][0]["message"]["content"],
            "model": selected_model
        }

    @staticmethod
    def list_models() -> dict:
        """Return all available Groq models"""
        return GroqProvider.AVAILABLE_MODELS