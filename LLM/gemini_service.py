"""
Google Gemini LLM service for MCP-Tools-Demo

Provides configured Gemini LLM instance for MCP Conductor agents.
"""

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_gemini_llm():
    """
    Initializes and returns a configured Gemini LLM instance.

    Returns:
        ChatGoogleGenerativeAI: Configured Gemini model instance

    Raises:
        ValueError: If GOOGLE_API_KEY is not set in environment
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY not found in environment variables. "
            "Please set your Google API key in .env file or environment."
        )

    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",  # Latest fast Gemini model
        temperature=0.1,  # Low temperature for consistency
        max_output_tokens=65536,  # Large context window
        google_api_key=api_key,
        max_retries=3,  # Retry logic for reliability
        timeout=120,  # 2-minute timeout
    )