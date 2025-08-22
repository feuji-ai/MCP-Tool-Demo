"""
MCP Client Manager for MCP-Tools-Demo

Simple MCP server management with filesystem default and custom server addition.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from mcp_conductor import MCPClient


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server."""
    name: str
    command: str
    args: List[str]
    env: Dict[str, str]
    description: str
    enabled: bool = False


class MCPServerManager:
    """Manages MCP servers with filesystem default and custom additions."""

    def __init__(self):
        """Initialize with ONLY filesystem server as default."""
        self.servers: Dict[str, MCPServerConfig] = {}
        self._load_filesystem_default()

    def _load_filesystem_default(self):
        """Load ONLY filesystem server as default."""
        current_dir = str(Path.cwd())
        self.servers["filesystem"] = MCPServerConfig(
            name="filesystem",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", current_dir],
            env={},
            description="File system operations - read, write, list files and directories",
            enabled=True  # Only default enabled
        )

    def get_available_servers(self) -> Dict[str, MCPServerConfig]:
        """Get all available server configurations."""
        return self.servers.copy()

    def get_enabled_servers(self) -> Dict[str, MCPServerConfig]:
        """Get only enabled server configurations."""
        return {name: config for name, config in self.servers.items() if config.enabled}

    def enable_server(self, server_name: str) -> bool:
        """Enable a server."""
        if server_name in self.servers:
            self.servers[server_name].enabled = True
            return True
        return False

    def disable_server(self, server_name: str) -> bool:
        """Disable a server."""
        if server_name in self.servers:
            self.servers[server_name].enabled = False
            return True
        return False

    def toggle_server(self, server_name: str) -> bool:
        """Toggle server enabled state."""
        if server_name in self.servers:
            self.servers[server_name].enabled = not self.servers[server_name].enabled
            return self.servers[server_name].enabled
        return False

    def set_server_selections(self, server_selections: Dict[str, bool]):
        """Set multiple server enabled states."""
        for server_name, enabled in server_selections.items():
            if server_name in self.servers:
                self.servers[server_name].enabled = enabled

    def add_custom_server(
        self,
        name: str,
        command: str,
        args: List[str],
        env: Optional[Dict[str, str]] = None,
        description: str = "",
        enabled: bool = False
    ) -> bool:
        """Add a custom MCP server configuration."""
        if name in self.servers:
            return False  # Server already exists

        self.servers[name] = MCPServerConfig(
            name=name,
            command=command,
            args=args,
            env=env or {},
            description=description,
            enabled=enabled
        )
        return True

    def remove_server(self, server_name: str) -> bool:
        """Remove a server configuration (except filesystem)."""
        if server_name == "filesystem":
            return False  # Can't remove filesystem default

        if server_name in self.servers:
            del self.servers[server_name]
            return True
        return False

    def update_filesystem_directories(self, directories: List[str]):
        """Update filesystem server with new directories."""
        if "filesystem" in self.servers:
            self.servers["filesystem"].args = ["-y", "@modelcontextprotocol/server-filesystem"] + directories

    def create_client_from_selection(self) -> MCPClient:
        """Create MCP client with currently enabled servers."""
        enabled_servers = self.get_enabled_servers()

        if not enabled_servers:
            # If nothing enabled, enable filesystem by default
            self.enable_server("filesystem")
            enabled_servers = {"filesystem": self.servers["filesystem"]}

        config = {"mcpServers": {}}

        for name, server_config in enabled_servers.items():
            config["mcpServers"][name] = {
                "command": server_config.command,
                "args": server_config.args,
                "env": server_config.env
            }

        return MCPClient.from_dict(config)

    def list_servers_for_selection(self) -> List[Dict[str, Any]]:
        """Get servers in format suitable for selection UI."""
        return [
            {
                "name": name,
                "description": config.description,
                "enabled": config.enabled,
                "command": f"{config.command} {' '.join(config.args)}"
            }
            for name, config in self.servers.items()
        ]


# Global manager instance
_server_manager = MCPServerManager()


def get_server_manager() -> MCPServerManager:
    """Get the global server manager instance."""
    return _server_manager


def create_filesystem_client(allowed_directories: Optional[List[str]] = None) -> MCPClient:
    """
    Create MCP client with ONLY filesystem server.

    Args:
        allowed_directories: List of directories to allow access to.
                           Defaults to current working directory.

    Returns:
        MCPClient: Configured client with filesystem server
    """
    if allowed_directories is None:
        allowed_directories = [str(Path.cwd())]

    config = {
        "mcpServers": {
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem"] + allowed_directories,
                "env": {}
            }
        }
    }

    return MCPClient.from_dict(config)


def add_custom_server(
    name: str,
    command: str,
    args: List[str],
    env: Optional[Dict[str, str]] = None,
    description: str = "",
    enabled: bool = False
) -> bool:
    """
    Add a custom MCP server to the available servers.

    Args:
        name: Unique name for the server
        command: Command to run the server
        args: Command line arguments
        env: Environment variables
        description: Human-readable description
        enabled: Whether to enable by default

    Returns:
        bool: True if added successfully, False if name already exists

    Example:
        add_custom_server(
            name="my_api_server",
            command="python",
            args=["-m", "my_mcp_server", "--port", "8080"],
            description="My custom API MCP server"
        )
    """
    manager = get_server_manager()
    return manager.add_custom_server(name, command, args, env, description, enabled)


def create_multi_server_client(server_selections: Optional[Dict[str, bool]] = None) -> MCPClient:
    """
    Create MCP client with multiple servers based on selections.

    Args:
        server_selections: Dict of server_name -> enabled status.
                          If None, uses current manager selections.

    Returns:
        MCPClient: Configured client with selected servers

    Example:
        # Select filesystem and your custom server
        client = create_multi_server_client({
            "filesystem": True,
            "my_api_server": True
        })
    """
    manager = get_server_manager()

    if server_selections:
        manager.set_server_selections(server_selections)

    return manager.create_client_from_selection()


def list_available_servers() -> List[Dict[str, Any]]:
    """
    List all available MCP servers.

    Returns:
        List: Server configurations for selection UI
    """
    manager = get_server_manager()
    return manager.list_servers_for_selection()


def print_server_status():
    """Print current server status."""
    manager = get_server_manager()
    servers = manager.list_servers_for_selection()

    print(f"\n📋 Available MCP Servers")
    print(f"═══════════════════════════")

    for server in servers:
        status = "✅" if server["enabled"] else "⬜"
        print(f"{status} {server['name']}")
        print(f"   📝 {server['description']}")
        print(f"   🔧 {server['command']}")
        print()

    enabled_count = sum(1 for s in servers if s["enabled"])
    print(f"📊 Total: {len(servers)} servers, {enabled_count} enabled")


# Quick setup functions for common use cases

def setup_basic_filesystem() -> MCPClient:
    """Quick setup with just filesystem."""
    return create_filesystem_client()


def setup_with_custom_servers(*custom_servers) -> MCPClient:
    """
    Quick setup with filesystem + custom servers.

    Args:
        *custom_servers: Tuples of (name, command, args, description)

    Example:
        client = setup_with_custom_servers(
            ("my_server", "python", ["-m", "my_server"], "My custom server")
        )
    """
    manager = get_server_manager()

    # Add custom servers
    for name, command, args, description in custom_servers:
        manager.add_custom_server(
            name=name,
            command=command,
            args=args,
            description=description,
            enabled=True
        )

    return manager.create_client_from_selection()


# Utility functions

def get_server_selection_dict() -> Dict[str, bool]:
    """Get current server selections as dict for UI."""
    manager = get_server_manager()
    return {name: config.enabled for name, config in manager.get_available_servers().items()}


def apply_server_selections(selections: Dict[str, bool]):
    """Apply server selections from UI."""
    manager = get_server_manager()
    manager.set_server_selections(selections)