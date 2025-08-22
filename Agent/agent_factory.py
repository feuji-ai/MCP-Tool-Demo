"""
Agent Factory - Simple agent creation functions

All functions return ready-to-use LangGraph agents with RICH display mode.
"""

from typing import Dict, Optional
from LLM import get_gemini_llm
from mcp_conductor import LangGraphAgent, StreamDisplayMode
from Client import create_multi_server_client, create_filesystem_client

def get_multi_server_agent(
        server_selections: Dict[str, bool],
        max_steps: int = 500
) -> LangGraphAgent:
    """
    Get agent with selected MCP servers.

    Args:
        server_selections: Dict of server_name -> enabled
        max_steps: Maximum execution steps

    Returns:
        LangGraphAgent: Ready agent with selected tools

    Example:
        agent = get_multi_server_agent({
            "filesystem": True,
            "my_custom_server": True
        })
    """
    llm = get_gemini_llm()
    client = create_multi_server_client(server_selections)

    return LangGraphAgent(
        llm=llm,
        client=client,
        max_steps=max_steps,
        stream_display_mode=StreamDisplayMode.RICH,
        auto_print_streaming=True,
        memory_enabled=True
    )
