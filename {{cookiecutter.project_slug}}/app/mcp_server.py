{% raw %}"""
MCP (Model Context Protocol) Server Implementation

This module provides MCP tools for remote AI clients to interact with
the FastAPI application and ML models via Cloudflare Tunnels.
"""{% endraw %}
{% if cookiecutter.enable_mcp_server == 'yes' %}
import os
from typing import Any, Dict, List

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
import mcp.types as types

from core.config import (
    PROJECT_NAME,
    VERSION,
    MODEL_NAME,
    MODEL_PATH,
)
from services.predict import MachineLearningModelHandlerScore as model_handler

# Initialize MCP Server
server = Server("{{ cookiecutter.mcp_server_name }}")


@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """
    List all available MCP tools exposed by this server.
    """
    return [
        types.Tool(
            name="predict",
            description="Execute ML model prediction with provided features",
            inputSchema={
                "type": "object",
                "properties": {
                    "features": {
                        "type": "array",
                        "description": "Array of feature values for prediction",
                        "items": {"type": "number"},
                    }
                },
                "required": ["features"],
            },
        ),
        types.Tool(
            name="health_check",
            description="Check server and model health status",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="get_model_info",
            description="Get information about the loaded ML model",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Dict[str, Any] | None
) -> List[types.TextContent]:
    """
    Handle tool execution requests from MCP clients.

    Args:
        name: Name of the tool to execute
        arguments: Tool-specific arguments

    Returns:
        List of TextContent responses
    """
    if name == "predict":
        return await handle_predict(arguments or {})
    elif name == "health_check":
        return await handle_health_check()
    elif name == "get_model_info":
        return await handle_model_info()
    else:
        raise ValueError(f"Unknown tool: {name}")


async def handle_predict(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """
    Execute ML model prediction.

    Args:
        arguments: Dict containing 'features' array

    Returns:
        Prediction result as TextContent
    """
    features = arguments.get("features")
    if not features:
        return [
            types.TextContent(
                type="text",
                text="Error: 'features' array is required for prediction",
            )
        ]

    try:
        # Initialize model handler
        ml_model = model_handler(MODEL_NAME, MODEL_PATH)

        # Make prediction
        prediction = ml_model.predict([features])

        result = {
            "prediction": prediction.tolist() if hasattr(prediction, "tolist") else prediction,
            "model": MODEL_NAME,
            "features_count": len(features),
        }

        return [
            types.TextContent(
                type="text",
                text=f"Prediction result: {result}",
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Prediction error: {str(e)}",
            )
        ]


async def handle_health_check() -> List[types.TextContent]:
    """
    Check server and model health.

    Returns:
        Health status as TextContent
    """
    try:
        # Try to load model to verify it's accessible
        ml_model = model_handler(MODEL_NAME, MODEL_PATH)
        model_loaded = ml_model.model is not None

        health_status = {
            "status": "healthy" if model_loaded else "degraded",
            "model_loaded": model_loaded,
            "model_name": MODEL_NAME,
            "version": VERSION,
            "server_name": PROJECT_NAME,
        }

        return [
            types.TextContent(
                type="text",
                text=f"Health check: {health_status}",
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Health check failed: {str(e)}",
            )
        ]


async def handle_model_info() -> List[types.TextContent]:
    """
    Get detailed model information.

    Returns:
        Model metadata as TextContent
    """
    try:
        model_info = {
            "model_name": MODEL_NAME,
            "model_path": MODEL_PATH,
            "model_full_path": os.path.join(MODEL_PATH, MODEL_NAME),
            "exists": os.path.exists(os.path.join(MODEL_PATH, MODEL_NAME)),
        }

        # Try to get model-specific info
        try:
            ml_model = model_handler(MODEL_NAME, MODEL_PATH)
            if hasattr(ml_model.model, "n_features_in_"):
                model_info["feature_count"] = ml_model.model.n_features_in_
            if hasattr(ml_model.model, "__class__"):
                model_info["model_type"] = str(ml_model.model.__class__)
        except Exception:
            pass

        return [
            types.TextContent(
                type="text",
                text=f"Model information: {model_info}",
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error retrieving model info: {str(e)}",
            )
        ]


# Export the server instance
__all__ = ["server"]
{% else %}
# MCP Server is disabled in this project
# To enable, set enable_mcp_server=yes in cookiecutter template
{% endif %}
