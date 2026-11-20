"""
A tiny MCP server with one tool: add two numbers.

Install once:
    pip install fastmcp

Quick test:
    python calculator_mcp_server.py 4 5   -> works like a normal calculator
    python calculator_mcp_server.py       -> starts the MCP server (waits for a client)
"""

import sys
from fastmcp import FastMCP

# Create the MCP server (its name and a short description for clients)
server = FastMCP(
    name="Calculator MCP Server",
    instructions="Simple MCP server exposing basic calculator tools.",
)


# Turn this function into a tool that other agents can call.
# The docstring becomes the tool description, so agents know when to use it.
@server.tool()
async def add(a: float, b: float) -> float:
    """Add two numbers and return the result."""
    return a + b


if __name__ == "__main__":
    # Two numbers given -> just calculate and print
    if len(sys.argv) == 3:
        print(float(sys.argv[1]) + float(sys.argv[2]))
    # No numbers -> run as an MCP server over stdio (no network port)
    else:
        server.run()
