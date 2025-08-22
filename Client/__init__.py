"""
MCP Connectors Package

Simple MCP server management with filesystem default and custom server addition.

Main functions:
- create_filesystem_client(): Get client with only filesystem
- add_custom_server(): Add your custom MCP servers
- create_multi_server_client(): Get client with selected servers
- list_available_servers(): List all available servers
- print_server_status(): Show current server status
"""

from .mcp_connectors import (
    # Core client creation
    create_filesystem_client,
    create_multi_server_client,

    # Custom server management
    add_custom_server,

    # Server information
    list_available_servers,
    print_server_status,
    get_server_manager,

    # Selection management
    get_server_selection_dict,
    apply_server_selections,

    # Quick setup utilities
    setup_basic_filesystem,
    setup_with_custom_servers,

    # Core classes (if needed)
    MCPServerManager,
    MCPServerConfig
)

__all__ = [
    # Main client functions
    "create_filesystem_client",
    "create_multi_server_client",

    # Server management
    "add_custom_server",

    # Information & status
    "list_available_servers",
    "print_server_status",
    "get_server_manager",

    # Selection utilities
    "get_server_selection_dict",
    "apply_server_selections",

    # Quick setup
    "setup_basic_filesystem",
    "setup_with_custom_servers",

    # Classes
    "MCPServerManager",
    "MCPServerConfig"
]