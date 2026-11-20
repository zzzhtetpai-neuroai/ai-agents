"""
An MCP client that connects to my Langflow MCP server (travel-tools),
lists its tools, and asks the healthy chef for a recipe.
This is what the MCP Tools box in the HungryTraveler flow does.

Install once:
    pip install mcp python-dotenv

Needs a .env file next to this script:
    LANGFLOW_MCP_URL=http://localhost:7860/api/v1/mcp/project/YOUR_PROJECT_ID/streamable
    LANGFLOW_API_KEY=your-langflow-api-key

Langflow must be running (langflow run) before you start this.
"""

import asyncio
import os

from dotenv import load_dotenv
from mcp.client.session import ClientSession
from mcp.client.streamable_http import create_mcp_http_client, streamable_http_client

# Read the server URL and API key from .env (keys never go in the code)
load_dotenv()
MCP_URL = os.environ["LANGFLOW_MCP_URL"]
API_KEY = os.environ["LANGFLOW_API_KEY"]


async def main() -> None:
    # An HTTP client that sends the API key with every request
    # (long timeout because the flows call OpenAI and can take a minute)
    http_client = create_mcp_http_client(headers={"x-api-key": API_KEY})
    http_client.timeout = 180

    # Connect to Langflow's MCP server over Streamable HTTP
    async with http_client, streamable_http_client(MCP_URL, http_client=http_client) as (read, write):
        async with ClientSession(read, write) as session:
            # Handshake
            await session.initialize()

            # Discovery: which flows are shared as tools?
            tools_response = await session.list_tools()
            print("Tools on travel-tools:")
            for tool in tools_response.tools:
                print(f"- {tool.name}: {tool.description or '(no description)'}")

            # Call the healthy chef flow like the agent did
            print("\nAsking the healthy chef...\n")
            result = await session.call_tool(
                "healthy_chef",
                {"input_value": "A healthy recipe inspired by Kyoto"},
            )

            # Print the text the flow returned
            for item in result.content:
                if getattr(item, "text", None):
                    print(item.text)


if __name__ == "__main__":
    asyncio.run(main())
