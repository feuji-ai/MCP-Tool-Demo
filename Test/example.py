#!/usr/bin/env python3
"""
Complete Multi-Server Example - Filesystem + Playwright MCP

This example demonstrates:
1. Starting with default filesystem MCP server
2. Adding Playwright MCP server using add_custom_server
3. Enabling both servers
4. Creating multi-server client
5. Creating agent with RICH display mode
6. Executing the complete workflow:
   - Read existing Test/Example/instructions.txt
   - Use Playwright to automate saucedemo.com
   - Save results to Test/Example/output.json

Prerequisites:
- Test/Example/instructions.txt must exist (you already have this)
- npm install -g @playwright/mcp@latest
- GOOGLE_API_KEY in .env file
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from Agent import get_multi_server_agent
from Client import (
    add_custom_server,
    get_server_manager,
    create_multi_server_client,
    print_server_status
)
from LLM import get_gemini_llm
from mcp_conductor import LangGraphAgent, StreamDisplayMode


def setup_test_environment():
    """Check that Test/Example directory and instructions.txt file already exist."""
    print("🔧 Checking test environment...")

    # Check Test/Example directory
    test_dir = Path("Test/Example")
    if not test_dir.exists():
        print(f"❌ Directory not found: {test_dir}")
        print("   Please create the Test/Example directory first")
        return None

    # Check instructions.txt
    instructions_file = test_dir / "instructions.txt"
    if not instructions_file.exists():
        print(f"❌ Instructions file not found: {instructions_file}")
        print("   Please create the instructions.txt file first")
        return None

    print(f"✅ Found existing directory: {test_dir}")
    print(f"✅ Found existing instructions: {instructions_file}")

    return test_dir


async def main():
    """Complete multi-server workflow example."""
    print("🚀 MCP Conductor - Multi-Server Example")
    print("🎯 Filesystem + Playwright MCP Integration")
    print("=" * 80)

    # Step 1: Verify test environment exists
    test_dir = setup_test_environment()
    if test_dir is None:
        print("❌ Test environment setup failed. Please check the requirements above.")
        return
    print()

    # Step 2: Add Playwright MCP server
    print("🎭 Step 2: Adding Playwright MCP Server...")
    success = add_custom_server(
        name="playwright",
        command="npx",
        args=["@playwright/mcp@latest"],
        env={},
        description="Browser automation - navigate, click, fill forms, take screenshots",
        enabled=False  # We'll enable it manually next
    )

    if success:
        print("✅ Playwright MCP server added successfully!")
    else:
        print("⚠️ Playwright server already exists (that's okay)")
    print()

    # Step 3: Enable both servers
    print("⚙️ Step 3: Enabling both servers...")
    manager = get_server_manager()

    # Enable filesystem (should already be enabled by default)
    manager.enable_server("filesystem")
    print("✅ Filesystem server enabled")

    # Enable playwright
    manager.enable_server("playwright")
    print("✅ Playwright server enabled")
    print()

    # Step 4: Show current server status
    print("📋 Step 4: Current Server Status")
    print_server_status()
    print()

    # Step 5: Create multi-server client
    print("🔗 Step 5: Creating multi-server client...")
    server_selections = {
        "filesystem": True,
        "playwright": True
    }
    client = create_multi_server_client(server_selections)
    print("✅ Multi-server client created")
    print()

    # Step 6: Create agent with RICH display mode
    print("🤖 Step 6: Creating LangGraph agent...")
    llm = get_gemini_llm()

    agent = LangGraphAgent(
        llm=llm,
        client=client,
        max_steps=50,  # Enough steps for the complete workflow
        stream_display_mode=StreamDisplayMode.RICH,  # Beautiful display
        auto_print_streaming=True,
        memory_enabled=True,
        verbose=True
        # No config_provider = no Langfuse observability
    )

    print("✅ Agent created with RICH display mode")
    print()

    # Step 7: Execute the complete workflow
    print("🎬 Step 7: Executing the complete workflow...")
    print("=" * 80)

    try:
        async with agent:
            # The main task that combines filesystem + playwright
            workflow_query = f"""
            Please execute the following multi-step workflow:

            1. **Read Instructions**: 
               - Read the file 'Test/Example/instructions.txt' to understand the task

            2. **Execute Browser Automation**:
               - Follow the instructions exactly as written in the file

            3. **Save Results**:
               - Format the extracted data as JSON according to the format specified in instructions
               - Save the JSON output to 'Test/Example/output.json'
               - Confirm the file was created successfully

            Please execute each step and provide detailed feedback on what you're doing.
            """

            print("🎯 Starting workflow execution...")
            result = await agent.run(workflow_query)

            print("\n" + "=" * 80)
            print("🎉 WORKFLOW COMPLETED!")
            print("=" * 80)

            # Step 8: Verify results
            output_file = test_dir / "output.json"
            if output_file.exists():
                print(f"✅ Output file created: {output_file}")
                print(f"📄 File size: {output_file.stat().st_size} bytes")

                # Show first 200 characters of the output
                content = output_file.read_text()
                preview = content[:200] + "..." if len(content) > 200 else content
                print(f"📝 Content preview:\n{preview}")
            else:
                print("⚠️ Output file not found - check the execution logs above")

            print(f"\n📊 Final result length: {len(result)} characters")

    except Exception as e:
        print(f"\n❌ Error during workflow execution: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🔧 Prerequisites check:")
    print("   📁 Make sure Test/Example/instructions.txt exists")
    print("   📦 Make sure you have: npm install -g @playwright/mcp@latest")
    print("   🔑 Make sure GOOGLE_API_KEY is set in your .env file")
    print("   🌐 Make sure you have internet connection for saucedemo.com")
    print()

    asyncio.run(main())