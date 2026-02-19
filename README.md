Arduino Chatbot API ##

AI-powered chatbot designed to help international school students learn Arduino,
electronics, and embedded programming in a simple, interactive, and safe way.
Built with FastAPI and supports multiple AI providers (Groq & OpenRouter).






=============================

Project Goal ##

The goal of this project is to create an educational AI assistant specialized in:

Teaching Arduino concepts

Explaining electronics components

Debugging Arduino code

Suggesting beginner-friendly projects

Guiding students step-by-step in building circuits

This chatbot is designed specifically for students, not general-purpose use.

===================================


Architecture Overview ##

Frontend (e.g., Streamlit)
        │
        ▼
FastAPI Backend (main.py)
        │
        ▼
Provider Router (Strategy Pattern)
        │
        ├── Groq Provider
        └── OpenRouter Provider


=======================================


Key Design Principles Used:

- Separation of Concerns

 -Strategy Pattern (Provider switching)

 -Environment-based configuration

 -Clean API design

 Modular provider structure

=======================================

AI System Behavior ##

The chatbot uses a strict Arduino-focused system prompt that ensures:

Only Arduino/electronics questions are answered

Simple explanations for school students

Code examples are provided when needed

Safety instructions are included when relevant

Unrelated topics are politely redirected


==========================================

Technologies Used  ##


FastAPI – Backend framework

Pydantic – Request/response validation

CORSMiddleware – Frontend communication

dotenv – Environment variable management

Groq API

OpenRouter API

==========================



Project Structure ##


AI-CHATBOT/
│
├── backend/
│   ├── providers/
│   │   ├── groq_provider.py
│   │   ├── openrouter_provider.py
│   │   └── __init__.py
│   │
│   ├── main.py
│
├── frontend/
│   └── app.py
│
├── .env
├── .env_example
├── requirements.txt
└── README.md
===============================

Multi-Provider Support ##

The chatbot allows switching between providers dynamically:

{
  "message": "How do I connect an ultrasonic sensor?",
  "provider": "groq"
}


Supported providers:

groq → Fast & optimized for student usage

openrouter → Access to multiple free models

This is implemented using a Provider Router (Strategy Pattern).
===========================


API Endpoints ##
🔹 GET /

Check if API is running

🔹 GET /health

Returns provider configuration status:

{
  "status": "ok",
  "providers": {
    "groq": true,
    "openrouter": false
  }
}

🔹 GET /providers

List supported providers and default models.

🔹 POST /chat

Main chat endpoint.

Request Example:
{
  "message": "Explain how LED works",
  "provider": "groq",
  "model": null,
  "conversation_history": []
}

Response Example:
{
  "response": "An LED is a Light Emitting Diode...",
  "provider": "groq",
  "model": "llama3-8b-8192"
}
