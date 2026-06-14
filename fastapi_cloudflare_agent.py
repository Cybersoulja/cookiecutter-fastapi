#!/usr/bin/env python3
"""
FastAPI Cookiecutter Agent for Cloudflare

An intelligent agent that helps users generate FastAPI projects from the cookiecutter
template and deploy them to Cloudflare infrastructure with MCP server support.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from anthropic import Anthropic
from anthropic.types.beta.beta_tool import BetaToolUnion


class FastAPICloudflareAgent:
    """Agent for generating and deploying FastAPI projects to Cloudflare."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the agent with Claude API client."""
        self.client = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        self.conversation_history = []
        self.project_context = {}

    def get_tools(self) -> List[BetaToolUnion]:
        """Define the tools available to the agent."""
        return [
            {
                "type": "custom",
                "name": "generate_fastapi_project",
                "description": "Generate a new FastAPI project from the cookiecutter template. Creates the project structure with ML model support, API routes, and configuration.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "project_name": {
                            "type": "string",
                            "description": "Name of the project (e.g., 'My ML API')"
                        },
                        "project_description": {
                            "type": "string",
                            "description": "Short description of the project"
                        },
                        "full_name": {
                            "type": "string",
                            "description": "Author's full name"
                        },
                        "email": {
                            "type": "string",
                            "description": "Author's email address"
                        },
                        "output_dir": {
                            "type": "string",
                            "description": "Directory where the project will be created",
                            "default": "."
                        }
                    },
                    "required": ["project_name", "project_description", "full_name", "email"]
                }
            },
            {
                "type": "custom",
                "name": "setup_mcp_server",
                "description": "Set up MCP (Model Context Protocol) server support in the FastAPI project. Adds SSE endpoints, MCP server configuration, and Cloudflare Tunnel integration.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the FastAPI project"
                        },
                        "mcp_server_name": {
                            "type": "string",
                            "description": "Name for the MCP server (e.g., 'fastapi-ml-server')"
                        },
                        "enable_cloudflare_tunnel": {
                            "type": "boolean",
                            "description": "Whether to set up Cloudflare Tunnel for secure access",
                            "default": True
                        }
                    },
                    "required": ["project_path", "mcp_server_name"]
                }
            },
            {
                "type": "custom",
                "name": "configure_cloudflare_deployment",
                "description": "Configure the project for deployment to Cloudflare infrastructure (Workers, Pages, or Tunnels). Sets up wrangler.toml, deployment scripts, and environment configuration.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the FastAPI project"
                        },
                        "deployment_type": {
                            "type": "string",
                            "enum": ["workers", "pages", "tunnel"],
                            "description": "Type of Cloudflare deployment: 'workers' for serverless functions, 'pages' for static + functions, 'tunnel' for exposing local server"
                        },
                        "cloudflare_account_id": {
                            "type": "string",
                            "description": "Cloudflare account ID (optional, can be set later)"
                        }
                    },
                    "required": ["project_path", "deployment_type"]
                }
            },
            {
                "type": "custom",
                "name": "install_dependencies",
                "description": "Install project dependencies using Poetry and set up the development environment.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the FastAPI project"
                        },
                        "include_dev": {
                            "type": "boolean",
                            "description": "Whether to install development dependencies",
                            "default": True
                        }
                    },
                    "required": ["project_path"]
                }
            },
            {
                "type": "custom",
                "name": "run_local_server",
                "description": "Start the FastAPI development server locally with hot reload.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the FastAPI project"
                        },
                        "port": {
                            "type": "integer",
                            "description": "Port to run the server on",
                            "default": 8080
                        },
                        "host": {
                            "type": "string",
                            "description": "Host to bind to",
                            "default": "0.0.0.0"
                        }
                    },
                    "required": ["project_path"]
                }
            },
            {
                "type": "custom",
                "name": "get_project_status",
                "description": "Get the current status of the project, including what's configured and what's missing.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the FastAPI project"
                        }
                    },
                    "required": ["project_path"]
                }
            }
        ]

    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool and return the result."""
        try:
            if tool_name == "generate_fastapi_project":
                return self._generate_project(tool_input)
            elif tool_name == "setup_mcp_server":
                return self._setup_mcp_server(tool_input)
            elif tool_name == "configure_cloudflare_deployment":
                return self._configure_cloudflare(tool_input)
            elif tool_name == "install_dependencies":
                return self._install_dependencies(tool_input)
            elif tool_name == "run_local_server":
                return self._run_local_server(tool_input)
            elif tool_name == "get_project_status":
                return self._get_project_status(tool_input)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}

    def _generate_project(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a FastAPI project from the cookiecutter template."""
        # Create cookiecutter input data
        cookiecutter_data = {
            "project_name": params["project_name"],
            "project_short_description": params["project_description"],
            "full_name": params["full_name"],
            "email": params["email"]
        }

        # Save to a temp file for cookiecutter
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(cookiecutter_data, f)
            config_file = f.name

        try:
            # Run cookiecutter
            output_dir = params.get("output_dir", ".")
            result = subprocess.run(
                ["cookiecutter", ".", "--no-input", "--config-file", config_file, "--output-dir", output_dir],
                cwd="/home/user/cookiecutter-fastapi",
                capture_output=True,
                text=True
            )

            os.unlink(config_file)

            if result.returncode == 0:
                project_slug = params["project_name"].lower().replace(' ', '-')
                project_path = os.path.join(output_dir, project_slug)
                self.project_context["project_path"] = project_path

                return {
                    "success": True,
                    "project_path": project_path,
                    "message": f"Successfully created FastAPI project at {project_path}",
                    "next_steps": [
                        "Run install_dependencies to set up the environment",
                        "Run setup_mcp_server to add MCP support",
                        "Run configure_cloudflare_deployment to set up deployment"
                    ]
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "message": "Failed to generate project"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _setup_mcp_server(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set up MCP server support in the project."""
        project_path = Path(params["project_path"])
        mcp_name = params["mcp_server_name"]
        enable_tunnel = params.get("enable_cloudflare_tunnel", True)

        if not project_path.exists():
            return {"success": False, "error": f"Project path {project_path} does not exist"}

        # Create MCP server configuration
        mcp_config = {
            "mcpServers": {
                mcp_name: {
                    "command": "uvx",
                    "args": ["mcp-server-sse", f"http://localhost:8080/mcp/sse"],
                    "transportType": "sse"
                }
            }
        }

        # Add MCP routes to the FastAPI app
        mcp_routes = '''"""MCP Server SSE endpoint for Claude Desktop integration."""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio
import json
from datetime import datetime

router = APIRouter()


@router.get("/mcp/sse")
async def mcp_sse_endpoint():
    """
    Server-Sent Events endpoint for MCP protocol.
    This allows Claude Desktop to connect to your FastAPI app as an MCP server.
    """
    async def event_stream():
        # Send initial connection event
        yield f"event: connected\\ndata: {json.dumps({'timestamp': datetime.utcnow().isoformat()})}\\n\\n"

        # Keep connection alive
        while True:
            await asyncio.sleep(30)
            yield f"event: ping\\ndata: {json.dumps({'timestamp': datetime.utcnow().isoformat()})}\\n\\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/mcp/tools")
async def list_mcp_tools():
    """List available MCP tools."""
    return {
        "tools": [
            {
                "name": "predict",
                "description": "Make predictions using the ML model",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "features": {
                            "type": "object",
                            "description": "Input features for prediction"
                        }
                    },
                    "required": ["features"]
                }
            }
        ]
    }
'''

        # Write MCP routes file
        mcp_routes_path = project_path / "app" / "api" / "routes" / "mcp.py"
        mcp_routes_path.write_text(mcp_routes)

        # Update main router to include MCP routes
        api_router_path = project_path / "app" / "api" / "routes" / "api.py"
        if api_router_path.exists():
            content = api_router_path.read_text()
            if "from app.api.routes import mcp" not in content:
                # Add import
                content = content.replace(
                    "from app.api.routes import predictor",
                    "from app.api.routes import predictor, mcp"
                )
                # Add router
                content = content.replace(
                    'router.include_router(predictor.router, tags=["Prediction"], prefix="/v1")',
                    'router.include_router(predictor.router, tags=["Prediction"], prefix="/v1")\n'
                    'router.include_router(mcp.router, tags=["MCP"], prefix="")'
                )
                api_router_path.write_text(content)

        # Create MCP config file for Claude Desktop
        config_path = project_path / "claude_desktop_config.json"
        config_path.write_text(json.dumps(mcp_config, indent=2))

        result = {
            "success": True,
            "message": f"MCP server '{mcp_name}' configured successfully",
            "config_path": str(config_path),
            "mcp_endpoint": "http://localhost:8080/mcp/sse",
            "next_steps": [
                "Start the server with run_local_server",
                f"Add the config from {config_path} to your Claude Desktop configuration"
            ]
        }

        if enable_tunnel:
            result["cloudflare_tunnel_setup"] = {
                "message": "To expose MCP server via Cloudflare Tunnel:",
                "steps": [
                    "Install cloudflared: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/",
                    "Run: cloudflared tunnel --url http://localhost:8080",
                    "Update claude_desktop_config.json with the tunnel URL"
                ]
            }

        return result

    def _configure_cloudflare(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Configure Cloudflare deployment."""
        project_path = Path(params["project_path"])
        deployment_type = params["deployment_type"]
        account_id = params.get("cloudflare_account_id", "YOUR_ACCOUNT_ID")

        if not project_path.exists():
            return {"success": False, "error": f"Project path {project_path} does not exist"}

        if deployment_type == "tunnel":
            # Create Cloudflare Tunnel configuration
            tunnel_config = {
                "tunnel": "fastapi-tunnel",
                "credentials-file": "/path/to/credentials.json",
                "ingress": [
                    {
                        "hostname": "api.example.com",
                        "service": "http://localhost:8080"
                    },
                    {
                        "service": "http_status:404"
                    }
                ]
            }

            config_path = project_path / "cloudflared.yml"
            import yaml
            with open(config_path, 'w') as f:
                yaml.dump(tunnel_config, f)

            return {
                "success": True,
                "deployment_type": "tunnel",
                "config_path": str(config_path),
                "message": "Cloudflare Tunnel configuration created",
                "next_steps": [
                    "Install cloudflared CLI",
                    "Run: cloudflared tunnel login",
                    "Run: cloudflared tunnel create fastapi-tunnel",
                    "Update cloudflared.yml with your credentials path",
                    "Run: cloudflared tunnel route dns fastapi-tunnel api.example.com",
                    "Run: cloudflared tunnel run fastapi-tunnel"
                ]
            }

        elif deployment_type == "workers":
            # Create wrangler.toml for Cloudflare Workers
            wrangler_config = f'''name = "fastapi-worker"
main = "src/index.py"
compatibility_date = "2024-01-01"

[env.production]
name = "fastapi-worker-production"
route = "api.example.com/*"

[vars]
ENVIRONMENT = "production"

account_id = "{account_id}"
'''

            config_path = project_path / "wrangler.toml"
            config_path.write_text(wrangler_config)

            # Create Workers adapter
            workers_adapter = '''"""Cloudflare Workers adapter for FastAPI."""

from app.main import app
from mangum import Mangum

# Wrap FastAPI app for Cloudflare Workers
handler = Mangum(app, lifespan="off")
'''

            src_path = project_path / "src"
            src_path.mkdir(exist_ok=True)
            (src_path / "index.py").write_text(workers_adapter)

            # Update pyproject.toml to include mangum
            pyproject_path = project_path / "pyproject.toml"
            if pyproject_path.exists():
                content = pyproject_path.read_text()
                if "mangum" not in content:
                    content = content.replace(
                        '[tool.poetry.group.aws.dependencies]',
                        '[tool.poetry.group.cloudflare]\noptional = true\n\n[tool.poetry.group.cloudflare.dependencies]'
                    )
                    content = content.replace(
                        '[tool.poetry.group.cloudflare.dependencies]',
                        '[tool.poetry.group.cloudflare.dependencies]\nmangum = "^0.17.0"'
                    )
                    pyproject_path.write_text(content)

            return {
                "success": True,
                "deployment_type": "workers",
                "config_path": str(config_path),
                "message": "Cloudflare Workers configuration created",
                "next_steps": [
                    "Install wrangler: npm install -g wrangler",
                    "Login: wrangler login",
                    f"Update account_id in {config_path}",
                    "Install mangum: poetry add --group cloudflare mangum",
                    "Deploy: wrangler deploy"
                ]
            }

        else:  # pages
            return {
                "success": False,
                "error": "Cloudflare Pages deployment not yet implemented for FastAPI (requires static frontend)"
            }

    def _install_dependencies(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Install project dependencies."""
        project_path = Path(params["project_path"])
        include_dev = params.get("include_dev", True)

        if not project_path.exists():
            return {"success": False, "error": f"Project path {project_path} does not exist"}

        try:
            # Install poetry if not available
            subprocess.run(["pip", "install", "--upgrade", "pip"], check=True)
            subprocess.run(["pip", "install", "poetry"], check=True)

            # Install dependencies
            cmd = ["poetry", "install"]
            if include_dev:
                cmd.append("--with")
                cmd.append("dev")

            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "message": "Dependencies installed successfully",
                    "next_steps": ["Run the server with run_local_server"]
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "message": "Failed to install dependencies"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _run_local_server(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Start the local development server."""
        project_path = Path(params["project_path"])
        port = params.get("port", 8080)
        host = params.get("host", "0.0.0.0")

        if not project_path.exists():
            return {"success": False, "error": f"Project path {project_path} does not exist"}

        return {
            "success": True,
            "message": f"To start the server, run this command in {project_path}:",
            "command": f"PYTHONPATH=app/ poetry run uvicorn main:app --reload --host {host} --port {port}",
            "endpoints": {
                "docs": f"http://localhost:{port}/docs",
                "redoc": f"http://localhost:{port}/redoc",
                "health": f"http://localhost:{port}/api/health",
                "mcp_sse": f"http://localhost:{port}/mcp/sse"
            },
            "note": "This command needs to be run in a terminal. The agent cannot start long-running processes."
        }

    def _get_project_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get the current project status."""
        project_path = Path(params["project_path"])

        if not project_path.exists():
            return {"success": False, "error": f"Project path {project_path} does not exist"}

        status = {
            "project_path": str(project_path),
            "exists": True,
            "components": {}
        }

        # Check for various components
        checks = {
            "pyproject.toml": "Poetry configuration",
            "app/main.py": "FastAPI application",
            "app/api/routes/mcp.py": "MCP server routes",
            "claude_desktop_config.json": "Claude Desktop MCP config",
            "wrangler.toml": "Cloudflare Workers config",
            "cloudflared.yml": "Cloudflare Tunnel config",
            ".env": "Environment configuration",
            "Dockerfile": "Docker configuration"
        }

        for file_path, description in checks.items():
            full_path = project_path / file_path
            status["components"][description] = {
                "configured": full_path.exists(),
                "path": str(full_path)
            }

        # Determine what's missing
        missing = [desc for desc, info in status["components"].items() if not info["configured"]]
        status["missing_components"] = missing
        status["next_steps"] = []

        if not status["components"]["MCP server routes"]["configured"]:
            status["next_steps"].append("Run setup_mcp_server to add MCP support")

        if not any([
            status["components"]["Cloudflare Workers config"]["configured"],
            status["components"]["Cloudflare Tunnel config"]["configured"]
        ]):
            status["next_steps"].append("Run configure_cloudflare_deployment to set up deployment")

        return {"success": True, "status": status}

    def chat(self, user_message: str) -> str:
        """
        Send a message to the agent and get a response.
        Uses adaptive thinking for complex reasoning.
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # System prompt for the agent
        system_prompt = """You are a helpful AI assistant specialized in FastAPI development and Cloudflare deployment.
You help users generate FastAPI projects from a cookiecutter template, set up MCP (Model Context Protocol) server support,
and deploy to Cloudflare infrastructure.

Your capabilities:
- Generate FastAPI projects with ML model support
- Configure MCP server endpoints for Claude Desktop integration
- Set up Cloudflare deployment (Workers, Tunnels)
- Guide users through the entire development and deployment process

When a user asks to create a project or deploy to Cloudflare, use your tools to help them step by step.
Be proactive in suggesting next steps and explaining what each component does.

Key concepts:
- MCP (Model Context Protocol): Allows Claude Desktop to connect to your FastAPI app as a tool server
- Cloudflare Tunnel: Securely exposes local development servers without opening ports
- Cloudflare Workers: Serverless deployment for FastAPI using Mangum adapter
"""

        # Make API call with tool use
        response = self.client.messages.create(
            model="claude-opus-4-8",
            max_tokens=4096,
            thinking={
                "type": "adaptive"
            },
            system=system_prompt,
            messages=self.conversation_history,
            tools=self.get_tools()
        )

        # Process the response
        assistant_message = {"role": "assistant", "content": []}
        text_response = []

        for block in response.content:
            if block.type == "thinking":
                # Store thinking blocks for replay
                assistant_message["content"].append(block)
            elif block.type == "text":
                text_response.append(block.text)
                assistant_message["content"].append(block)
            elif block.type == "tool_use":
                # Execute the tool
                tool_result = self.execute_tool(block.name, block.input)

                # Add tool use to assistant message
                assistant_message["content"].append(block)

                # Add tool result to conversation
                self.conversation_history.append(assistant_message)
                self.conversation_history.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(tool_result)
                    }]
                })

                # Get next response after tool execution
                return self.chat("")  # Recursively continue the conversation

        # Add assistant message to history
        self.conversation_history.append(assistant_message)

        return "\n".join(text_response)


def main():
    """Main entry point for the agent."""
    print("🚀 FastAPI Cookiecutter Agent for Cloudflare")
    print("=" * 60)
    print("I can help you generate FastAPI projects and deploy them to Cloudflare.")
    print("Type 'quit' to exit.\n")

    agent = FastAPICloudflareAgent()

    while True:
        try:
            user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break

            print("\nAgent: ", end="", flush=True)
            response = agent.chat(user_input)
            print(response)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
