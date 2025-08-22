"""
LLM service module for MCP-Tools-Demo

Provides language model integrations for MCP Conductor agents.
"""

from .gemini_service import get_gemini_llm

__all__ = [
    "get_gemini_llm"
]