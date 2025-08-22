#!/usr/bin/env python3
"""
REAL MCP Conductor WebSocket Server for Demo directory

This version uses actual MCP Conductor integration instead of simulation.
Integrates with the same Client and Agent modules used in example.py
"""

import asyncio
import json
import logging
import traceback
import websockets
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Add parent directory to path for imports (we're in Demo/ folder now)
sys.path.append(str(Path(__file__).parent.parent))

# Import real MCP modules (from parent directory)
from Client import (
    add_custom_server,
    get_server_manager,
    create_multi_server_client,
    print_server_status,
    list_available_servers
)
from Agent import get_multi_server_agent
from LLM import get_gemini_llm
from mcp_conductor import LangGraphAgent, StreamDisplayMode

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('RealMCPWebSocketServer')


class RealMCPWebSocketServer:
    """Real MCP WebSocket server with actual MCP Conductor integration."""

    def __init__(self):
        self.connected_clients = set()
        self.agent: LangGraphAgent = None
        self.agent_ready = False
        self.server_manager = get_server_manager()

    async def send_to_client(self, websocket, message: dict):
        """Send message to client."""
        try:
            await websocket.send(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending to client: {e}")

    async def send_server_list_update(self, websocket):
        """Send updated server list to client."""
        try:
            servers = list_available_servers()
            await self.send_to_client(websocket, {
                "type": "server_list_update",
                "servers": servers,
                "total_count": len(servers),
                "enabled_count": sum(1 for s in servers if s["enabled"])
            })
        except Exception as e:
            logger.error(f"Error sending server list: {e}")

    async def handle_start_agent(self, websocket):
        """Initialize REAL MCP agent"""
        try:
            await self.send_to_client(websocket, {
                "type": "log",
                "message": "🚀 Starting Real MCP Conductor Agent",
                "level": "info"
            })

            await self.send_to_client(websocket, {
                "type": "status",
                "status": "busy",
                "icon": "🟡",
                "text": "Initializing..."
            })

            # Get enabled servers
            enabled_servers = self.server_manager.get_enabled_servers()
            if not enabled_servers:
                await self.send_to_client(websocket, {
                    "type": "error",
                    "message": "No servers enabled! Please enable at least one server."
                })
                return

            await self.send_to_client(websocket, {
                "type": "log",
                "message": f"📋 Found {len(enabled_servers)} enabled servers",
                "level": "info"
            })

            # Create real multi-server client
            server_selections = {name: True for name in enabled_servers.keys()}
            client = create_multi_server_client(server_selections)

            await self.send_to_client(websocket, {
                "type": "log",
                "message": "🔗 Creating MCP client with enabled servers...",
                "level": "info"
            })

            # Create real LangGraph agent with STEALTH mode for demo
            llm = get_gemini_llm()
            self.agent = LangGraphAgent(
                llm=llm,
                client=client,
                max_steps=50,
                stream_display_mode=StreamDisplayMode.STEALTH,  # 🥷 STEALTH mode for demo
                auto_print_streaming=False,  # We'll capture and send via WebSocket
                memory_enabled=True,
                verbose=False
            )

            await self.send_to_client(websocket, {
                "type": "log",
                "message": "🤖 Initializing agent and connecting to MCP servers...",
                "level": "info"
            })

            # Initialize the real agent
            await self.agent.initialize()

            await self.send_to_client(websocket, {
                "type": "log",
                "message": "✅ Real MCP agent initialized successfully!",
                "level": "success"
            })

            await self.send_to_client(websocket, {
                "type": "status",
                "status": "ready",
                "icon": "🟢",
                "text": "Ready"
            })

            await self.send_to_client(websocket, {
                "type": "agent_ready"
            })

            self.agent_ready = True
            logger.info("✅ Real MCP agent is ready!")

        except Exception as e:
            error_msg = f"Failed to initialize real agent: {str(e)}"
            logger.error(error_msg)
            traceback.print_exc()

            await self.send_to_client(websocket, {
                "type": "error",
                "message": error_msg
            })

            await self.send_to_client(websocket, {
                "type": "status",
                "status": "error",
                "icon": "🔴",
                "text": "Error"
            })

    async def handle_execute_query(self, websocket, message: str):
        """Execute real query using MCP agent with STEALTH mode streaming"""
        if not self.agent_ready or not self.agent:
            await self.send_to_client(websocket, {
                "type": "error",
                "message": "No agent initialized. Please start the agent first."
            })
            return

        try:
            await self.send_to_client(websocket, {
                "type": "log",
                "message": f"🥷 STEALTH EXECUTION: {message[:50]}{'...' if len(message) > 50 else ''}",
                "level": "info"
            })

            await self.send_to_client(websocket, {
                "type": "status",
                "status": "busy",
                "icon": "🟡",
                "text": "🥷 Stealth Processing..."
            })

            # Send STEALTH execution header
            await self.send_to_client(websocket, {
                "type": "stealth_header",
                "query": message,
                "thread_id": self.agent.thread_id if hasattr(self.agent, 'thread_id') else "stealth-session"
            })

            # Execute REAL agent streaming with STEALTH mode capture
            step_count = 0
            tool_execution_count = 0
            final_result = ""

            async for item in self.agent.stream(message):
                if isinstance(item, dict):
                    if item.get("type") == "tool_call":
                        step_count += 1
                        tool_execution_count += 1

                        # Send STEALTH tool execution step
                        await self.send_to_client(websocket, {
                            "type": "stealth_step",
                            "step_number": step_count,
                            "execution_number": tool_execution_count,
                            "tool_name": item.get("tool_name", "unknown"),
                            "tool_input": str(item.get("tool_input", ""))[:200],
                            "message": f"🥷 Step {step_count} - STEALTH TOOL EXECUTION #{tool_execution_count}"
                        })

                        await self.send_to_client(websocket, {
                            "type": "log",
                            "message": f"🛠️ STEALTH Tool: {item.get('tool_name', 'unknown')}",
                            "level": "info"
                        })

                    elif item.get("type") == "tool_result":
                        content = str(item.get("content", ""))
                        content_preview = content[:150] + "..." if len(content) > 150 else content
                        content_preview = content_preview.replace('\n', ' ')

                        # Send STEALTH tool result
                        await self.send_to_client(websocket, {
                            "type": "stealth_result",
                            "step_number": step_count,
                            "content_preview": content_preview,
                            "content_length": len(content)
                        })

                        await self.send_to_client(websocket, {
                            "type": "log",
                            "message": f"✅ STEALTH Output: {content_preview}",
                            "level": "success"
                        })

                    elif item.get("type") == "ai_message":
                        content = item.get("content", "")
                        if content and len(content.strip()) > 10:  # Only show substantial AI reasoning
                            content_preview = content[:100] + "..." if len(content) > 100 else content
                            content_preview = content_preview.replace('\n', ' ')

                            # Send STEALTH AI reasoning
                            await self.send_to_client(websocket, {
                                "type": "stealth_reasoning",
                                "content": content_preview
                            })

                            await self.send_to_client(websocket, {
                                "type": "log",
                                "message": f"🤖 STEALTH AI: {content_preview}",
                                "level": "info"
                            })

                elif isinstance(item, str):
                    # Final result
                    final_result = item
                    break

            # Send STEALTH completion summary
            await self.send_to_client(websocket, {
                "type": "stealth_complete",
                "total_steps": step_count,
                "tool_executions": tool_execution_count,
                "success": bool(final_result and not final_result.startswith('Error:'))
            })

            # Send final result
            await self.send_to_client(websocket, {
                "type": "chat_response",
                "message": final_result or "STEALTH mission completed but produced no output."
            })

            await self.send_to_client(websocket, {
                "type": "log",
                "message": f"🥷 STEALTH MISSION COMPLETE - {step_count} steps, {tool_execution_count} tool executions",
                "level": "success"
            })

            await self.send_to_client(websocket, {
                "type": "status",
                "status": "ready",
                "icon": "🟢",
                "text": "Ready"
            })

        except Exception as e:
            error_msg = f"STEALTH mission failed: {str(e)}"
            logger.error(error_msg)
            traceback.print_exc()

            await self.send_to_client(websocket, {
                "type": "error",
                "message": error_msg
            })

            await self.send_to_client(websocket, {
                "type": "status",
                "status": "ready",
                "icon": "🟢",
                "text": "Ready"
            })

    async def handle_add_server(self, websocket, data):
        """Handle add server requests using real server manager"""
        server_name = data.get("name", "unknown")
        command = data.get("command", "")
        args = data.get("args", [])
        description = data.get("description", "")

        await self.send_to_client(websocket, {
            "type": "log",
            "message": f"🎭 Adding {server_name} server: {command} {' '.join(args)}",
            "level": "info"
        })

        # Use REAL server manager
        success = add_custom_server(
            name=server_name,
            command=command,
            args=args,
            description=description,
            enabled=False  # Add but don't enable by default
        )

        if success:
            await self.send_to_client(websocket, {
                "type": "log",
                "message": f"✅ {server_name} server added successfully!",
                "level": "success"
            })
        else:
            await self.send_to_client(websocket, {
                "type": "log",
                "message": f"⚠️ {server_name} server already exists",
                "level": "warning"
            })

        # Send updated server list
        await self.send_server_list_update(websocket)

    async def handle_toggle_server(self, websocket, data):
        """Handle server toggle requests using real server manager"""
        server_name = data.get("name", "unknown")
        enabled = data.get("enabled", False)

        if enabled:
            success = self.server_manager.enable_server(server_name)
        else:
            success = self.server_manager.disable_server(server_name)

        if success:
            status = "enabled" if enabled else "disabled"
            await self.send_to_client(websocket, {
                "type": "log",
                "message": f"⚙️ Server '{server_name}' {status}",
                "level": "info"
            })
        else:
            await self.send_to_client(websocket, {
                "type": "log",
                "message": f"⌐ Failed to toggle server '{server_name}'",
                "level": "error"
            })

        # Send updated server list
        await self.send_server_list_update(websocket)

    async def handle_check_instructions(self, websocket):
        """Handle check instructions requests using real filesystem"""
        await self.send_to_client(websocket, {
            "type": "log",
            "message": "📋 Checking for instructions file using real filesystem...",
            "level": "info"
        })

        # Check if agent is ready
        if not self.agent_ready or not self.agent:
            await self.send_to_client(websocket, {
                "type": "error",
                "message": "Please start the agent first to use filesystem tools."
            })
            return

        # Use real agent to read instructions
        try:
            query = "Please read the file 'Test/Example/instructions.txt' and show me its contents."

            await self.send_to_client(websocket, {
                "type": "log",
                "message": "📖 Reading instructions.txt using real filesystem tools...",
                "level": "info"
            })

            result = await self.agent.run(query)

            await self.send_to_client(websocket, {
                "type": "chat_response",
                "message": f"📄 Instructions File Content:\n\n{result}"
            })

        except Exception as e:
            await self.send_to_client(websocket, {
                "type": "error",
                "message": f"Failed to read instructions: {str(e)}"
            })

    async def handle_message(self, websocket, message: str):
        """Handle incoming messages"""
        try:
            data = json.loads(message)
            message_type = data.get("type")

            logger.info(f"Received message type: {message_type}")

            if message_type == "start_agent":
                await self.handle_start_agent(websocket)
            elif message_type == "execute_query":
                await self.handle_execute_query(websocket, data.get("message", ""))
            elif message_type == "reset_agent":
                # Reset real agent
                if self.agent:
                    await self.agent.close()
                self.agent = None
                self.agent_ready = False

                await self.send_to_client(websocket, {
                    "type": "status",
                    "status": "error",
                    "icon": "🔴",
                    "text": "Not Ready"
                })
                await self.send_to_client(websocket, {
                    "type": "log",
                    "message": "🔄 Real agent reset",
                    "level": "info"
                })
            elif message_type == "add_server":
                await self.handle_add_server(websocket, data)
            elif message_type == "toggle_server":
                await self.handle_toggle_server(websocket, data)
            elif message_type == "check_instructions":
                await self.handle_check_instructions(websocket)
            elif message_type == "get_server_list":
                # Send current server list
                await self.send_server_list_update(websocket)
            else:
                await self.send_to_client(websocket, {
                    "type": "log",
                    "message": f"⚠️ Unknown message type: {message_type}",
                    "level": "warning"
                })

        except Exception as e:
            logger.error(f"Error handling message: {e}")
            traceback.print_exc()
            await self.send_to_client(websocket, {
                "type": "error",
                "message": f"Server error: {str(e)}"
            })

    async def handle_client(self, websocket):
        """Handle client connection"""
        client_address = websocket.remote_address
        self.connected_clients.add(websocket)
        logger.info(f"Client connected from {client_address}. Total clients: {len(self.connected_clients)}")

        # Send initial status
        await self.send_to_client(websocket, {
            "type": "log",
            "message": "Connected to Real MCP Conductor backend",
            "level": "success"
        })

        await self.send_to_client(websocket, {
            "type": "status",
            "status": "error",
            "icon": "🔴",
            "text": "Not Ready"
        })

        # Send initial server list
        await self.send_server_list_update(websocket)

        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {client_address} disconnected normally")
        except Exception as e:
            logger.error(f"Error with client {client_address}: {e}")
        finally:
            # Clean up agent if this was the last client
            if self.agent and len(self.connected_clients) <= 1:
                try:
                    await self.agent.close()
                    self.agent = None
                    self.agent_ready = False
                    logger.info("🧹 Cleaned up agent on last client disconnect")
                except Exception as e:
                    logger.error(f"Error cleaning up agent: {e}")

            self.connected_clients.discard(websocket)
            logger.info(f"Client {client_address} removed. Total clients: {len(self.connected_clients)}")


async def main():
    """Start the real MCP WebSocket server"""
    server = RealMCPWebSocketServer()

    print("🚀 Starting REAL MCP Conductor WebSocket Server")
    print("🔐 Now with Password Manager support!")
    print("🔗 This version uses actual MCP integration!")
    print("🔡 Server: ws://localhost:8765")
    print("🌐 Open demo.html in your browser")
    print("=" * 60)

    try:
        # Start the server
        async with websockets.serve(
                server.handle_client,
                "localhost",
                8765,
                ping_interval=20,
                ping_timeout=10,
                close_timeout=10
        ):
            print("✅ Real MCP Server started successfully!")
            print("🔗 WebSocket endpoint: ws://localhost:8765")
            print("📊 Waiting for connections...")
            print("🔐 Password Manager ready for demo!")
            await asyncio.Future()  # Run forever

    except Exception as e:
        print(f"⌐ Server failed to start: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Real MCP Server stopped by user")
    except Exception as e:
        print(f"⌐ Fatal error: {e}")
        traceback.print_exc()