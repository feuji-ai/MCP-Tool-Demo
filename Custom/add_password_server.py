"""
Password Server Integration for MCP-Tools-Demo

Easy integration of the custom password manager MCP server.
"""

import sys
from pathlib import Path

# Add parent directory to path for Client imports
sys.path.append(str(Path(__file__).parent.parent))

from Client import add_custom_server, get_server_manager


def add_password_server(enabled: bool = False) -> bool:
    """
    Add the password manager MCP server to available servers.

    Args:
        enabled: Whether to enable the server by default

    Returns:
        bool: True if added successfully, False if already exists

    Example:
        # Add password server (disabled by default)
        add_password_server()

        # Add and enable password server
        add_password_server(enabled=True)
    """
    # Get the path to the password server script
    custom_dir = Path(__file__).parent
    server_script = custom_dir / "password_server.py"

    if not server_script.exists():
        raise FileNotFoundError(f"Password server script not found: {server_script}")

    success = add_custom_server(
        name="password_manager",
        command="python",
        args=[str(server_script)],
        env={},
        description="Password management - generate, save, encrypt/decrypt passwords securely",
        enabled=enabled
    )

    return success


def setup_password_server() -> bool:
    """
    Quick setup: add and enable password server.

    Returns:
        bool: True if setup was successful

    Example:
        from Custom import setup_password_server
        setup_password_server()
    """
    success = add_password_server(enabled=False)

    if success:
        print("✅ Password manager server added successfully!")
    else:
        print("ℹ️ Password manager server already exists")

    # Enable it
    manager = get_server_manager()
    manager.enable_server("password_manager")
    print("✅ Password manager server enabled")

    return True


def get_password_server_config() -> dict:
    """
    Get the configuration dict for the password server.
    Useful for manual client creation.

    Returns:
        dict: Server configuration
    """
    custom_dir = Path(__file__).parent
    server_script = custom_dir / "password_server.py"

    return {
        "command": "python",
        "args": [str(server_script)],
        "env": {}
    }


# Demo function for easy testing
def demo_password_workflow():
    """
    Demo function showing password manager usage.
    This can be called from the web interface.
    """
    print("🔐 Password Manager Demo Workflow:")
    print("1. Generate a secure password")
    print("2. Save it for a service (e.g., 'Gmail')")
    print("3. Retrieve it later")
    print("4. List all saved passwords")
    print()
    print("💡 Try these commands in the agent:")
    print("  - 'Generate a 16-character password with symbols'")
    print("  - 'Save a password for Gmail with username john@example.com'")
    print("  - 'Get the password for Gmail'")
    print("  - 'List all my saved passwords'")


if __name__ == "__main__":
    # Quick test/demo
    print("🔐 Password Manager MCP Server Setup")
    print("=" * 50)

    try:
        setup_password_server()
        print("\n✅ Setup complete!")
        print("\n💡 You can now use password management tools in your agent:")
        demo_password_workflow()

    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback

        traceback.print_exc()