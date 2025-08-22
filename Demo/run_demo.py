#!/usr/bin/env python3
"""
Updated Demo Launcher with Real MCP Integration

Serves demo.html via HTTP server and starts the REAL MCP WebSocket server.
"""

import subprocess
import webbrowser
import time
import threading
import http.server
import socketserver
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def start_http_server(demo_dir):
    """Start HTTP server to serve demo.html from the correct directory"""
    PORT = 8080

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(demo_dir), **kwargs)

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🌐 HTTP Server started on http://localhost:{PORT}")
        print(f"📂 Serving files from: {demo_dir}")
        httpd.serve_forever()


def start_real_websocket_server(demo_dir):
    """Start the REAL WebSocket server with MCP integration"""
    import asyncio

    # Import the real WebSocket server (in Demo/ directory)
    real_server_file = demo_dir / "websocket_server.py"

    if real_server_file.exists():
        # Import and run the real server
        try:
            # Add Demo directory to path for local imports
            sys.path.insert(0, str(demo_dir))
            from websocket_server import main as server_main
            asyncio.run(server_main())
        except ImportError as e:
            print(f"❌ Failed to import real WebSocket server: {e}")
            print("   Make sure all dependencies are installed:")
            print("   - mcp_conductor")
            print("   - Client module (../Client)")
            print("   - Agent module (../Agent)")
            print("   - LLM module (../LLM)")
    else:
        print(f"❌ Real WebSocket server file not found: {real_server_file}")


def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking prerequisites...")

    issues = []

    # Determine the correct paths based on where script is run from
    script_dir = Path(__file__).parent

    # If run from parent directory, demo files are in Demo/ subdirectory
    if script_dir.name == "Demo":
        # Running from Demo/ directory
        demo_dir = script_dir
        parent_dir = script_dir.parent
    else:
        # Running from parent directory
        demo_dir = script_dir / "Demo"
        parent_dir = script_dir

    # Check files exist
    required_files = [
        demo_dir / "websocket_server.py",  # In Demo/ directory
        demo_dir / "demo.html",  # In Demo/ directory
        parent_dir / "Client" / "__init__.py",
        parent_dir / "Agent" / "__init__.py",
        parent_dir / "LLM" / "__init__.py"
    ]

    for file_path in required_files:
        if not Path(file_path).exists():
            issues.append(f"❌ Missing file: {file_path}")
        else:
            print(f"✅ Found: {file_path}")

    # Check environment
    if not os.getenv("GOOGLE_API_KEY"):
        issues.append("❌ GOOGLE_API_KEY not set in environment")
    else:
        print("✅ GOOGLE_API_KEY is set")

    # Check if Test/Example directory exists (in parent directory)
    test_dir = parent_dir / "Test" / "Example"
    if test_dir.exists():
        print(f"✅ Found test directory: {test_dir}")

        instructions_file = test_dir / "instructions.txt"
        if instructions_file.exists():
            print(f"✅ Found instructions file: {instructions_file}")
        else:
            print(f"⚠️  Instructions file not found: {instructions_file}")
    else:
        print(f"⚠️  Test directory not found: {test_dir}")

    return issues, demo_dir


def main():
    """Launch the demo with real MCP integration"""
    print("🎼 MCP Conductor Demo Launcher (REAL INTEGRATION)")
    print("=" * 55)

    # Check prerequisites and get demo directory
    issues, demo_dir = check_prerequisites()

    if issues:
        print("\n❌ Prerequisites check failed:")
        for issue in issues:
            print(f"   {issue}")
        print("\nPlease fix these issues before running the demo.")
        return

    print("\n✅ All prerequisites satisfied!")
    print(f"📂 Demo directory: {demo_dir}")

    # Check if demo.html exists
    demo_file = demo_dir / "demo.html"
    if not demo_file.exists():
        print(f"❌ demo.html not found in {demo_dir}!")
        return

    print("✅ demo.html found")

    # Start HTTP server in background thread
    print("🌐 Starting HTTP server...")
    http_thread = threading.Thread(target=lambda: start_http_server(demo_dir), daemon=True)
    http_thread.start()

    # Wait a moment for HTTP server to start
    time.sleep(1)

    # Start REAL WebSocket server in background thread
    print("🚀 Starting REAL MCP WebSocket server...")
    ws_thread = threading.Thread(target=lambda: start_real_websocket_server(demo_dir), daemon=True)
    ws_thread.start()

    # Wait for servers to start
    time.sleep(3)

    # Open browser to HTTP URL
    demo_url = "http://localhost:8080/demo.html"
    print(f"🌐 Opening: {demo_url}")
    webbrowser.open(demo_url)

    print("\n✅ Demo running with REAL MCP integration + STEALTH MODE!")
    print("📡 WebSocket: ws://localhost:8765 (Real MCP)")
    print("🌐 Web Server: http://localhost:8080")
    print("🔧 Demo URL: http://localhost:8080/demo.html")
    print(f"📂 Serving from: {demo_dir}")
    print("\n💡 Features available:")
    print("   🗂️  Real filesystem operations")
    print("   🎭 Real Playwright browser automation")
    print("   🤖 Real LangGraph agent with STEALTH streaming")
    print("   📊 Real-time execution logs")
    print("   🥷 STEALTH mode with hidden query privacy")
    print("\n🎯 Test with:")
    print("   📋 'Read Test/Example/instructions.txt and execute the task'")
    print("   🌐 'Navigate to saucedemo.com and login with standard_user'")
    print("\nPress Ctrl+C to stop...")

    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Demo stopped")


if __name__ == "__main__":
    main()