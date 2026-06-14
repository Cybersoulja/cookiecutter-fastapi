# cookiecutter-fastapi

A template for creating FastAPI projects with ML model support, MCP server integration, and Cloudflare deployment. :rocket:

## ✨ New: AI-Powered Agent

Use the FastAPI Cloudflare Agent to generate and deploy projects with natural language:

```bash
pip install -r agent_requirements.txt
export ANTHROPIC_API_KEY="your-key"
python fastapi_cloudflare_agent.py
```

Then interact naturally:
```
You: Create a FastAPI project for image classification
Agent: I'll generate that for you...

You: Add MCP server support for Claude Desktop
Agent: Setting up MCP endpoints...

You: Deploy it to Cloudflare
Agent: Configuring deployment...
```

See [AGENT_README.md](AGENT_README.md) for full documentation.

## Important
To use this project you don't need fork it. Just run cookiecutter CLI and voilà!

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
