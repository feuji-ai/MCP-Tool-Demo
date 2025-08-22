"""
Agent package - Simple agent creation

Import and use:
    from agent import get_filesystem_agent, get_multi_server_agent

All agents use RICH display mode by default.
"""

from .agent_factory import (
    get_multi_server_agent,
)

__all__ = [
    "get_multi_server_agent",
]