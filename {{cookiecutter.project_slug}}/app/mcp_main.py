{% raw %}"""
MCP Server Entry Point with SSE (Server-Sent Events) Transport

This module sets up the FastAPI application with MCP SSE transport
for remote AI clients accessing via Cloudflare Tunnels.
"""{% endraw %}
{% if cookiecutter.enable_mcp_server == 'yes' %}
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.sse import SseServerTransport
from sse_starlette.sse import EventSourceResponse
from loguru import logger

from core.config import (
    PROJECT_NAME,
    VERSION,
    DEBUG,
    API_PREFIX,
)
from mcp_server import server as mcp_server

# Configure allowed origins for CORS
ALLOWED_ORIGINS = [
    "https://api.anthropic.com",
    "https://claude.ai",
    "http://localhost:3000",  # Development
    "http://localhost:8000",  # Development
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    """
    logger.info(f"Starting MCP Server: {PROJECT_NAME} v{VERSION}")
    logger.info(f"MCP Endpoint: {{ cookiecutter.mcp_endpoint }}")
    yield
    logger.info("Shutting down MCP Server")


# Create FastAPI application
app = FastAPI(
    title=f"{PROJECT_NAME} - MCP Server",
    description="Model Context Protocol Server for AI Assistant Integration",
    version=VERSION,
    debug=DEBUG,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Create SSE transport
sse_transport = SseServerTransport("{{ cookiecutter.mcp_endpoint }}")


@app.get("/")
async def root():
    """
    Root endpoint with server information.
    """
    return {
        "name": PROJECT_NAME,
        "version": VERSION,
        "mcp_endpoint": "{{ cookiecutter.mcp_endpoint }}",
        "status": "running",
        "transport": "sse",
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {
        "status": "healthy",
        "service": "mcp-server",
        "version": VERSION,
    }


@app.get("{{ cookiecutter.mcp_endpoint }}")
async def handle_sse_get(request: Request):
    """
    Handle SSE GET requests for MCP protocol.

    This endpoint is used by MCP clients to establish SSE connection.
    """
    async def event_generator():
        async with sse_transport.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            read_stream, write_stream = streams

            # Run the MCP server with the connected streams
            async with mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            ):
                # Keep connection alive
                await asyncio.Event().wait()

    return EventSourceResponse(event_generator())


@app.post("{{ cookiecutter.mcp_endpoint }}")
async def handle_sse_post(request: Request):
    """
    Handle SSE POST requests for MCP protocol.

    This endpoint handles MCP messages sent via POST.
    """
    message = await request.json()

    # Process the MCP message
    async with sse_transport.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        read_stream, write_stream = streams

        # Send message to MCP server
        await write_stream.send(message)

        # Get response
        response = await read_stream.receive()

        return response


@app.get(f"{API_PREFIX}/")
async def api_root():
    """
    API root endpoint (maintains compatibility with base template).
    """
    return {
        "message": "MCP Server API",
        "version": VERSION,
        "mcp_endpoint": "{{ cookiecutter.mcp_endpoint }}",
    }


# Include the original FastAPI routes if needed
from api.routes.api import router as api_router
app.include_router(api_router, prefix=API_PREFIX)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "mcp_main:app",
        host="0.0.0.0",
        port=8000,
        reload=DEBUG,
        log_level="debug" if DEBUG else "info",
    )
{% else %}
# MCP Server is disabled
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {
        "message": "MCP Server is not enabled in this project",
        "note": "Regenerate with enable_mcp_server=yes to enable MCP support"
    }
{% endif %}
