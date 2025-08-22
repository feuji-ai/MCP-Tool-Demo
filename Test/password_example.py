#!/usr/bin/env python3
"""
Password Manager Example

Quick example showing how to use the custom password manager MCP server.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from Agent import get_multi_server_agent
from Client import add_custom_server, get_server_manager, create_multi_server_client
from Custom import add_password_server, setup_password_server
from LLM import get_gemini_llm
from mcp_conductor import LangGraphAgent, StreamDisplayMode


async def main():
    """Demo the password manager functionality."""
    print("🔐 Password Manager MCP Server Demo")
    print("=" * 50)

    # Step 1: Add password server
    print("📦 Step 1: Adding password manager server...")
    setup_password_server()
    print()

    # Step 2: Also enable filesystem for saving to files if needed
    print("📁 Step 2: Enabling filesystem server...")
    manager = get_server_manager()
    manager.enable_server("filesystem")
    print("✅ Filesystem server enabled")
    print()

    # Step 3: Create client with selected servers
    print("🔗 Step 3: Creating multi-server client...")
    server_selections = {
        "filesystem": True,
        "password_manager": True
    }
    client = create_multi_server_client(server_selections)
    print("✅ Client created with filesystem + password manager")
    print()

    # Step 4: Create agent
    print("🤖 Step 4: Creating agent...")
    llm = get_gemini_llm()

    agent = LangGraphAgent(
        llm=llm,
        client=client,
        max_steps=20,
        stream_display_mode=StreamDisplayMode.RICH,
        auto_print_streaming=True,
        memory_enabled=True
    )
    print("✅ Agent created with RICH display")
    print()

    # Step 5: Demo password management workflow
    print("🎯 Step 5: Testing password management workflow...")
    print("=" * 50)

    try:
        async with agent:
            # Test 1: Generate a password
            print("\n🔑 Test 1: Generate a secure password")
            result1 = await agent.run("Generate a 16-character password with symbols")
            print(f"Result: {result1[:100]}...")

            # Test 2: Save a password (YES, we ARE testing save here!)
            print("\n💾 Test 2: Save a password for a service")
            result2 = await agent.run("""
            Save a password for Gmail with:
            - Service: Gmail
            - Username: demo@example.com  
            - Password: MySecurePassword123!
            - URL: https://gmail.com
            - Notes: Personal email account
            """)
            print(f"Result: {result2[:100]}...")

            # Test 3: List saved passwords
            print("\n📋 Test 3: List all saved passwords")
            result3 = await agent.run("List all my saved passwords")
            print(f"Result: {result3[:200]}...")

            # Test 4: Retrieve a password
            print("\n🔓 Test 4: Retrieve the Gmail password")
            result4 = await agent.run("Get the password for Gmail")
            print(f"Result: {result4[:200]}...")

            # Test 5: Update a password
            print("\n🔄 Test 5: Update the Gmail password")
            result5 = await agent.run(
                "Update the Gmail password to 'NewSecurePassword456!' and change notes to 'Updated password'")
            print(f"Result: {result5[:200]}...")

            # Test 6: Generate and save another password
            print("\n🔑 Test 6: Generate and save a GitHub password")
            result6 = await agent.run("""
            First generate a 20-character password with symbols, then save it for GitHub with:
            - Service: GitHub
            - Username: myuser
            - URL: https://github.com
            - Notes: Development account
            """)
            print(f"Result: {result6[:200]}...")

            # Small delay to help with cleanup
            print("\n⏳ Allowing cleanup time...")
            await asyncio.sleep(1)

    except Exception as e:
        print(f"❌ Error during demo: {e}")

    print("\n✅ Password manager demo completed!")
    print("\n🔐 What we tested:")
    print("   ✅ Generate secure passwords")
    print("   ✅ Save passwords with metadata")
    print("   ✅ List all saved passwords")
    print("   ✅ Retrieve specific passwords")
    print("   ✅ Update existing passwords")
    print("   ✅ Generate and save in one step")

    print("\n💡 Try these commands in the web demo:")
    print("   - 'Generate a 20-character password with symbols'")
    print("   - 'Save a password for GitHub with username myuser'")
    print("   - 'List all my saved passwords'")
    print("   - 'Get the password for GitHub'")
    print("   - 'Delete the password for Gmail'")
    print("   - 'Update the GitHub password'")

    # Final delay to help with subprocess cleanup
    await asyncio.sleep(0.5)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
    finally:
        print("🧹 Demo cleanup complete")