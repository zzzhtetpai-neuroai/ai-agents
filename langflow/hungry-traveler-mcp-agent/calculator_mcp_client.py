"""
An MCP client that starts the calculator server, lists its tools,
and calls the add tool. This is what Langflow's MCP Tools component does for us.

Install once:
    pip install fastmcp mcp

Run (keep calculator_mcp_server.py in the same folder):
    python calculator_mcp_client.py
"""

import asyncio
import sys
from pathlib import Path

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

# Path to the server script (same folder as this file)
SERVER_SCRIPT = str(Path(__file__).parent / "calculator_mcp_server.py")


async def main() -> None:
    # How to start the server: run the server script with this same Python
    server_params = StdioServerParameters(command=sys.executable, args=[SERVER_SCRIPT])

    # Start the server in the background and open a channel to it
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Handshake: say hello before asking for anything
            await session.initialize()

            # Discovery: ask the server which tools it has
            tools_response = await session.list_tools()
            print("Available tools on the server:")
            for tool in tools_response.tools:
                print(f"- {tool.name}: {tool.description or '(no description)'}")

            # Call the add tool, like an agent would
            result = await session.call_tool("add", {"a": 4.0, "b": 3.0})
            print("\nRaw MCP tool result:")
            print(result)

            # Pull the number out of the result
            # (newer mcp versions call it structured_content, older ones structuredContent)
            data = getattr(result, "structured_content", None) or getattr(result, "structuredContent", None)
            value = data.get("result") if data else None
            print(f"\n4 + 3 = {value}")


if __name__ == "__main__":
    asyncio.run(main())
