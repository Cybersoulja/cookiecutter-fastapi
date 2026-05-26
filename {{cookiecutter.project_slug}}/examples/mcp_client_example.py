{% raw %}"""
MCP Client Example

This script demonstrates how to connect to and use the MCP server
from a Python client application.

Install requirements:
    pip install mcp httpx

Usage:
    python examples/mcp_client_example.py
"""{% endraw %}
{% if cookiecutter.enable_mcp_server == 'yes' %}
import asyncio
import os
from typing import Any, Dict

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    import httpx
except ImportError:
    print("Error: Required packages not installed.")
    print("Install with: pip install mcp httpx")
    exit(1)


# Configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000{{ cookiecutter.mcp_endpoint }}")
MCP_API_KEY = os.getenv("MCP_API_KEY", "your-api-key-here")


async def call_mcp_tool_http(
    tool_name: str, arguments: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Call an MCP tool using direct HTTP requests.

    This is a simple example that doesn't use the full MCP SDK.
    """
    async with httpx.AsyncClient() as client:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {MCP_API_KEY}",
        }

        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments,
            },
            "id": 1,
        }

        try:
            response = await client.post(
                MCP_SERVER_URL,
                json=payload,
                headers=headers,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"HTTP error occurred: {e}")
            return {"error": str(e)}


async def example_health_check():
    """
    Example: Check server health.
    """
    print("\n=== Health Check Example ===")
    result = await call_mcp_tool_http("health_check", {})
    print(f"Result: {result}")


async def example_model_info():
    """
    Example: Get model information.
    """
    print("\n=== Model Info Example ===")
    result = await call_mcp_tool_http("get_model_info", {})
    print(f"Result: {result}")


async def example_prediction():
    """
    Example: Make a prediction.
    """
    print("\n=== Prediction Example ===")

    # Sample features - adjust based on your model
    features = [1.5, 2.3, 4.1, 0.8, 3.2, 1.1, 2.7, 0.5]

    result = await call_mcp_tool_http("predict", {"features": features})
    print(f"Features: {features}")
    print(f"Result: {result}")


async def example_with_mcp_sdk():
    """
    Example using the full MCP SDK with SSE transport.

    Note: This requires the MCP server to be running with SSE support.
    """
    print("\n=== MCP SDK Example (SSE) ===")

    try:
        from mcp.client.sse import sse_client

        async with sse_client(MCP_SERVER_URL) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                await session.initialize()

                # List available tools
                tools = await session.list_tools()
                print(f"Available tools: {[tool.name for tool in tools.tools]}")

                # Call a tool
                result = await session.call_tool("health_check", {})
                print(f"Health check result: {result}")

    except Exception as e:
        print(f"MCP SDK example failed: {e}")
        print("Make sure the MCP server is running and SSE is enabled.")


async def main():
    """
    Run all examples.
    """
    print(f"Connecting to MCP Server: {MCP_SERVER_URL}")
    print(f"Using API Key: {MCP_API_KEY[:10]}..." if len(MCP_API_KEY) > 10 else "No API key set")

    # Run HTTP-based examples
    await example_health_check()
    await example_model_info()
    await example_prediction()

    # Uncomment to try MCP SDK example
    # await example_with_mcp_sdk()

    print("\n=== Examples Complete ===")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
{% else %}
print("MCP Server is not enabled in this project.")
print("Regenerate with enable_mcp_server=yes to enable MCP support.")
{% endif %}
