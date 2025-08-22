#!/usr/bin/env python3
"""
Password Manager MCP Server

A secure MCP server for password management with:
- generate_password: Generate secure passwords
- save_password: Save encrypted password with metadata
- get_password: Retrieve and decrypt password
- list_passwords: List all saved password entries
- delete_password: Delete a saved password entry

Uses Fernet encryption for secure password storage.
"""

import asyncio
import json
import secrets
import string
from pathlib import Path
from typing import Any, Dict, List
import base64
from datetime import datetime

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource
import mcp.types as types
from cryptography.fernet import Fernet

# Server instance
server = Server("password-manager")

# Storage file
STORAGE_FILE = Path.home() / ".mcp_passwords.json"
KEY_FILE = Path.home() / ".mcp_password_key"


def get_or_create_key() -> bytes:
    """Get or create encryption key."""
    if KEY_FILE.exists():
        return KEY_FILE.read_bytes()
    else:
        key = Fernet.generate_key()
        KEY_FILE.write_bytes(key)
        KEY_FILE.chmod(0o600)  # Owner read/write only
        print(f"🔐 Created new encryption key at {KEY_FILE}")
        return key


def encrypt_password(password: str) -> str:
    """Encrypt password using Fernet."""
    key = get_or_create_key()
    f = Fernet(key)
    encrypted = f.encrypt(password.encode('utf-8'))
    return base64.b64encode(encrypted).decode('utf-8')


def decrypt_password(encrypted_password: str) -> str:
    """Decrypt password using Fernet."""
    key = get_or_create_key()
    f = Fernet(key)
    encrypted_bytes = base64.b64decode(encrypted_password.encode('utf-8'))
    decrypted = f.decrypt(encrypted_bytes)
    return decrypted.decode('utf-8')


def load_passwords() -> Dict[str, Any]:
    """Load passwords from storage file."""
    if not STORAGE_FILE.exists():
        return {}

    try:
        with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_passwords(passwords: Dict[str, Any]):
    """Save passwords to storage file."""
    with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
        json.dump(passwords, f, indent=2)

    # Set secure permissions
    STORAGE_FILE.chmod(0o600)


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available password management tools."""
    return [
        Tool(
            name="generate_password",
            description="Generate a secure random password",
            inputSchema={
                "type": "object",
                "properties": {
                    "length": {
                        "type": "integer",
                        "description": "Password length (default: 16)",
                        "default": 16,
                        "minimum": 8,
                        "maximum": 128
                    },
                    "include_symbols": {
                        "type": "boolean",
                        "description": "Include special symbols (default: true)",
                        "default": True
                    },
                    "include_numbers": {
                        "type": "boolean",
                        "description": "Include numbers (default: true)",
                        "default": True
                    },
                    "include_uppercase": {
                        "type": "boolean",
                        "description": "Include uppercase letters (default: true)",
                        "default": True
                    },
                    "include_lowercase": {
                        "type": "boolean",
                        "description": "Include lowercase letters (default: true)",
                        "default": True
                    }
                }
            }
        ),
        Tool(
            name="save_password",
            description="Save an encrypted password with metadata",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "description": "Service/website/app name (e.g., 'Gmail', 'GitHub')"
                    },
                    "username": {
                        "type": "string",
                        "description": "Username or email for this service"
                    },
                    "password": {
                        "type": "string",
                        "description": "Password to encrypt and save"
                    },
                    "url": {
                        "type": "string",
                        "description": "Website URL (optional)"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Additional notes (optional)"
                    }
                },
                "required": ["service", "username", "password"]
            }
        ),
        Tool(
            name="get_password",
            description="Retrieve and decrypt a saved password",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "description": "Service/website/app name to retrieve password for"
                    }
                },
                "required": ["service"]
            }
        ),
        Tool(
            name="list_passwords",
            description="List all saved password entries (without revealing passwords)",
            inputSchema={
                "type": "object",
                "properties": {
                    "show_details": {
                        "type": "boolean",
                        "description": "Show detailed information including URLs and notes (default: true)",
                        "default": True
                    }
                }
            }
        ),
        Tool(
            name="delete_password",
            description="Delete a saved password entry",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "description": "Service/website/app name to delete"
                    }
                },
                "required": ["service"]
            }
        ),
        Tool(
            name="update_password",
            description="Update an existing password entry",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "description": "Service/website/app name to update"
                    },
                    "username": {
                        "type": "string",
                        "description": "New username (optional - keeps existing if not provided)"
                    },
                    "password": {
                        "type": "string",
                        "description": "New password (optional - keeps existing if not provided)"
                    },
                    "url": {
                        "type": "string",
                        "description": "New website URL (optional)"
                    },
                    "notes": {
                        "type": "string",
                        "description": "New notes (optional)"
                    }
                },
                "required": ["service"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> List[
    types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls."""

    if name == "generate_password":
        length = arguments.get("length", 16)
        include_symbols = arguments.get("include_symbols", True)
        include_numbers = arguments.get("include_numbers", True)
        include_uppercase = arguments.get("include_uppercase", True)
        include_lowercase = arguments.get("include_lowercase", True)

        # Build character set based on options
        chars = ""
        if include_lowercase:
            chars += string.ascii_lowercase
        if include_uppercase:
            chars += string.ascii_uppercase
        if include_numbers:
            chars += string.digits
        if include_symbols:
            chars += "!@#$%^&*()-_=+[]{}|;:,.<>?"

        if not chars:
            return [types.TextContent(type="text", text="❌ Error: At least one character type must be included!")]

        # Generate password
        password = ''.join(secrets.choice(chars) for _ in range(length))

        # Ensure at least one character from each enabled set (if length allows)
        if length >= 2:
            password_list = list(password)
            pos = 0

            if include_lowercase and pos < length:
                password_list[pos] = secrets.choice(string.ascii_lowercase)
                pos += 1
            if include_uppercase and pos < length:
                password_list[pos] = secrets.choice(string.ascii_uppercase)
                pos += 1
            if include_numbers and pos < length:
                password_list[pos] = secrets.choice(string.digits)
                pos += 1
            if include_symbols and pos < length:
                password_list[pos] = secrets.choice("!@#$%^&*()-_=+[]{}|;:,.<>?")
                pos += 1

            # Shuffle to randomize positions
            secrets.SystemRandom().shuffle(password_list)
            password = ''.join(password_list)

        result = f"🔐 Generated secure password: {password}\n\n"
        result += f"📏 Length: {length} characters\n"
        result += f"🔤 Lowercase: {'✅' if include_lowercase else '❌'}\n"
        result += f"🔠 Uppercase: {'✅' if include_uppercase else '❌'}\n"
        result += f"🔢 Numbers: {'✅' if include_numbers else '❌'}\n"
        result += f"🎭 Symbols: {'✅' if include_symbols else '❌'}\n"
        result += f"\n💡 Tip: Use 'save_password' to store this securely!"

        return [types.TextContent(type="text", text=result)]

    elif name == "save_password":
        service = arguments["service"]
        username = arguments["username"]
        password = arguments["password"]
        url = arguments.get("url", "")
        notes = arguments.get("notes", "")

        # Load existing passwords
        passwords = load_passwords()

        try:
            # Encrypt the password
            encrypted_password = encrypt_password(password)

            # Create entry
            current_time = datetime.now().isoformat()
            entry = {
                "username": username,
                "encrypted_password": encrypted_password,
                "url": url,
                "notes": notes,
                "created_at": current_time,
                "updated_at": current_time
            }

            # Save entry
            passwords[service] = entry
            save_passwords(passwords)

            result = f"✅ Password saved successfully!\n\n"
            result += f"🏷️ Service: {service}\n"
            result += f"👤 Username: {username}\n"
            result += f"🔒 Encryption: Fernet (AES 128)\n"
            if url:
                result += f"🌐 URL: {url}\n"
            if notes:
                result += f"📝 Notes: {notes}\n"
            result += f"📅 Saved: {current_time}\n"
            result += f"\n💡 Use 'get_password' with service='{service}' to retrieve it later."

            return [types.TextContent(type="text", text=result)]

        except Exception as e:
            result = f"❌ Failed to save password: {str(e)}"
            return [types.TextContent(type="text", text=result)]

    elif name == "get_password":
        service = arguments["service"]

        # Load passwords
        passwords = load_passwords()

        if service not in passwords:
            available_services = list(passwords.keys())
            result = f"❌ No password found for service '{service}'\n\n"
            if available_services:
                result += f"📋 Available services: {', '.join(available_services)}\n"
                result += f"💡 Use 'list_passwords' to see all entries."
            else:
                result += "💡 No passwords saved yet. Use 'save_password' to add one."
            return [types.TextContent(type="text", text=result)]

        entry = passwords[service]

        try:
            # Decrypt password
            decrypted_password = decrypt_password(entry["encrypted_password"])

            result = f"🔓 Password retrieved for {service}:\n\n"
            result += f"👤 Username: {entry['username']}\n"
            result += f"🔑 Password: {decrypted_password}\n"
            if entry.get("url"):
                result += f"🌐 URL: {entry['url']}\n"
            if entry.get("notes"):
                result += f"📝 Notes: {entry['notes']}\n"
            result += f"📅 Updated: {entry.get('updated_at', 'Unknown')}\n"
            result += f"\n⚠️ Handle this password securely!"

            return [types.TextContent(type="text", text=result)]

        except Exception as e:
            result = f"❌ Failed to decrypt password for '{service}': {str(e)}\n"
            result += f"💡 The password may be corrupted or encrypted with a different key."
            return [types.TextContent(type="text", text=result)]

    elif name == "list_passwords":
        show_details = arguments.get("show_details", True)
        passwords = load_passwords()

        if not passwords:
            result = "📝 No passwords saved yet.\n\n"
            result += "💡 Use 'generate_password' to create a secure password\n"
            result += "💡 Use 'save_password' to store it securely"
            return [types.TextContent(type="text", text=result)]

        result = f"🔐 Password Manager - Saved Entries ({len(passwords)} total):\n\n"

        for service, entry in passwords.items():
            result += f"🏷️ {service}\n"
            result += f"   👤 Username: {entry['username']}\n"

            if show_details:
                if entry.get("url"):
                    result += f"   🌐 URL: {entry['url']}\n"
                if entry.get("notes"):
                    notes_preview = entry['notes'][:100] + "..." if len(entry.get('notes', '')) > 100 else entry.get(
                        'notes', '')
                    result += f"   📝 Notes: {notes_preview}\n"
                result += f"   📅 Updated: {entry.get('updated_at', 'Unknown')}\n"

            result += "\n"

        result += f"💡 Use 'get_password' with any service name to retrieve the password.\n"
        result += f"💡 Use 'delete_password' to remove an entry.\n"
        result += f"💡 Use 'update_password' to modify an existing entry."

        return [types.TextContent(type="text", text=result)]

    elif name == "delete_password":
        service = arguments["service"]

        # Load passwords
        passwords = load_passwords()

        if service not in passwords:
            available_services = list(passwords.keys())
            result = f"❌ No password found for service '{service}'\n\n"
            if available_services:
                result += f"📋 Available services: {', '.join(available_services)}"
            return [types.TextContent(type="text", text=result)]

        # Delete the entry
        deleted_entry = passwords.pop(service)
        save_passwords(passwords)

        result = f"🗑️ Password deleted successfully!\n\n"
        result += f"🏷️ Service: {service}\n"
        result += f"👤 Username: {deleted_entry['username']}\n"
        result += f"📅 Was created: {deleted_entry.get('created_at', 'Unknown')}\n"
        result += f"\n⚠️ This action cannot be undone!"

        return [types.TextContent(type="text", text=result)]

    elif name == "update_password":
        service = arguments["service"]

        # Load passwords
        passwords = load_passwords()

        if service not in passwords:
            available_services = list(passwords.keys())
            result = f"❌ No password found for service '{service}'\n\n"
            if available_services:
                result += f"📋 Available services: {', '.join(available_services)}"
            return [types.TextContent(type="text", text=result)]

        # Get existing entry
        entry = passwords[service]

        try:
            # Update fields if provided
            updated_fields = []

            if "username" in arguments and arguments["username"]:
                entry["username"] = arguments["username"]
                updated_fields.append("username")

            if "password" in arguments and arguments["password"]:
                entry["encrypted_password"] = encrypt_password(arguments["password"])
                updated_fields.append("password")

            if "url" in arguments:
                entry["url"] = arguments["url"]
                updated_fields.append("url")

            if "notes" in arguments:
                entry["notes"] = arguments["notes"]
                updated_fields.append("notes")

            # Update timestamp
            entry["updated_at"] = datetime.now().isoformat()

            # Save
            passwords[service] = entry
            save_passwords(passwords)

            result = f"✅ Password entry updated successfully!\n\n"
            result += f"🏷️ Service: {service}\n"
            result += f"🔄 Updated fields: {', '.join(updated_fields) if updated_fields else 'none'}\n"
            result += f"📅 Updated: {entry['updated_at']}\n"

            if not updated_fields:
                result += f"\n💡 No changes were made (no new values provided)."

            return [types.TextContent(type="text", text=result)]

        except Exception as e:
            result = f"❌ Failed to update password entry: {str(e)}"
            return [types.TextContent(type="text", text=result)]

    else:
        return [types.TextContent(type="text", text=f"❌ Unknown tool: {name}")]


async def main():
    """Run the password manager MCP server."""
    print("🔐 Password Manager MCP Server starting...")
    print(f"📁 Storage: {STORAGE_FILE}")
    print(f"🔑 Key file: {KEY_FILE}")
    print("🔒 Encryption: Fernet (AES 128)")

    # Ensure key exists
    get_or_create_key()

    # Read from stdin, write to stdout
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="password-manager",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    import mcp.server.stdio

    asyncio.run(main())