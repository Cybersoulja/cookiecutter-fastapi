# cookiecutter-fastapi

A production-ready Cookiecutter template for FastAPI projects with ML model serving and MCP (Model Context Protocol) support. :rocket:

## Features

- ⚡ **FastAPI** - Modern, fast web framework for building APIs
- 🤖 **ML Model Serving** - Built-in support for serving machine learning models
- 🌐 **MCP Server** - Optional Model Context Protocol server for AI agent integration
- 🔒 **Cloudflare Tunnels** - Secure remote access via Cloudflare infrastructure
- 🐳 **Docker Ready** - Production-ready containerization
- ☁️ **Multi-Cloud Deploy** - Support for AWS Lambda and GCP Cloud Run
- 🧪 **Testing Suite** - Pre-configured pytest setup
- 📝 **Auto Documentation** - Swagger/ReDoc API documentation

## Important
To use this project you don't need to fork it. Just run cookiecutter CLI and voilà!

## Cookiecutter

Cookiecutter is a CLI tool (Command Line Interface) to create an application boilerplate from a template. It uses a templating system — Jinja2 — to replace or customize folder and file names, as well as file content.

### How can I install?

```bash
pip install cookiecutter
```

### How can I generate a FastAPI project?

```bash
cookiecutter gh:arthurhenrique/cookiecutter-fastapi
```

### Hands On

![Example](./docs/example/cookiecutter-fastapi-cli.svg)

## MCP Server Support (New!)

Enable **Model Context Protocol (MCP)** support to expose your FastAPI application to remote AI clients like Claude via secure Cloudflare Tunnels.

### What is MCP?

MCP allows AI assistants to securely invoke your API endpoints and ML models as tools, enabling powerful AI-driven workflows.

### Quick Start

When generating your project, select `yes` for `enable_mcp_server`:

```bash
cookiecutter gh:arthurhenrique/cookiecutter-fastapi
# ... answer prompts ...
enable_mcp_server [yes]: yes
```

Then in your generated project:

```bash
# Install MCP dependencies
make install-mcp

# Run MCP server
make run-mcp

# Create Cloudflare Tunnel (for remote access)
make tunnel-dev
```

### Documentation

Complete MCP setup guide available in generated projects:
- `docs/MCP_CLOUDFLARE_SETUP.md` - Full setup and deployment guide
- `docs/MCP_SECURITY.md` - Security best practices
- `mcp-client-config.example.json` - Client configuration
- `examples/mcp_client_example.py` - Python client example

### Available MCP Tools

Generated projects expose these tools to AI clients:
- **predict** - Execute ML model predictions
- **health_check** - Server and model health status
- **get_model_info** - Model metadata and information

### Architecture

```
Remote AI Client → Cloudflare Edge → Tunnel → Local FastAPI + MCP Server
```

See [docs/MCP_CLOUDFLARE_SETUP.md](docs/MCP_CLOUDFLARE_SETUP.md) for detailed architecture and setup.
