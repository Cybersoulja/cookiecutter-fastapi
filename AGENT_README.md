# FastAPI Cookiecutter Agent for Cloudflare

An intelligent AI agent powered by Claude that helps you generate FastAPI projects and deploy them to Cloudflare infrastructure with MCP (Model Context Protocol) server support.

## Features

- 🤖 **AI-Powered Assistance**: Natural language interaction for project generation and deployment
- 🚀 **FastAPI Project Generation**: Create production-ready FastAPI projects from the cookiecutter template
- 🔧 **MCP Server Setup**: Automatic configuration of MCP endpoints for Claude Desktop integration
- ☁️ **Cloudflare Deployment**: Support for Workers, Pages, and Tunnels
- 🛠️ **Tool Use**: Agent uses Claude's tool use capabilities to execute tasks
- 💭 **Adaptive Thinking**: Leverages Claude Opus 4.8's adaptive thinking for complex reasoning

## Quick Start

### Prerequisites

- Python 3.9+
- Anthropic API key (get one at https://console.anthropic.com/)
- Poetry (for dependency management)
- Cloudflare account (for deployment)

### Installation

```bash
# Clone or navigate to the cookiecutter-fastapi directory
cd cookiecutter-fastapi

# Install agent dependencies
pip install -r agent_requirements.txt

# Set your Anthropic API key
export ANTHROPIC_API_KEY="your-api-key-here"
```

### Usage

#### Interactive Mode

```bash
python fastapi_cloudflare_agent.py
```

Then interact with the agent:

```
You: Create a new FastAPI project called "ML Predictions API" for image classification

Agent: I'll help you create that project! Let me generate it with the cookiecutter template...
[Agent generates project, sets up structure, provides next steps]

You: Now set up MCP server support so I can use it with Claude Desktop

Agent: I'll configure the MCP server endpoints...
[Agent adds MCP routes, creates config files, explains integration]

You: Deploy it to Cloudflare using Tunnels

Agent: I'll set up Cloudflare Tunnel configuration...
[Agent creates tunnel config, provides deployment instructions]
```

#### Programmatic Usage

```python
from fastapi_cloudflare_agent import FastAPICloudflareAgent

# Initialize the agent
agent = FastAPICloudflareAgent(api_key="your-api-key")

# Have a conversation
response = agent.chat("Create a FastAPI project for a sentiment analysis API")
print(response)

# Continue the conversation
response = agent.chat("Add MCP server support and configure for Cloudflare Workers")
print(response)
```

## Agent Capabilities

The agent has access to the following tools:

### 1. `generate_fastapi_project`

Generates a new FastAPI project from the cookiecutter template.

**Parameters:**
- `project_name`: Name of the project
- `project_description`: Short description
- `full_name`: Author's full name
- `email`: Author's email
- `output_dir`: Directory for project creation (default: current directory)

### 2. `setup_mcp_server`

Sets up MCP (Model Context Protocol) server support in the FastAPI project.

**Parameters:**
- `project_path`: Path to the FastAPI project
- `mcp_server_name`: Name for the MCP server
- `enable_cloudflare_tunnel`: Whether to include Tunnel setup (default: true)

**What it does:**
- Adds `/mcp/sse` endpoint for Server-Sent Events
- Creates `/mcp/tools` endpoint for tool discovery
- Generates `claude_desktop_config.json` for Claude Desktop
- Integrates MCP routes into the FastAPI app

### 3. `configure_cloudflare_deployment`

Configures the project for Cloudflare deployment.

**Parameters:**
- `project_path`: Path to the FastAPI project
- `deployment_type`: `"workers"`, `"pages"`, or `"tunnel"`
- `cloudflare_account_id`: Your Cloudflare account ID (optional)

**Deployment Types:**
- **Workers**: Serverless FastAPI deployment using Mangum adapter
- **Tunnel**: Secure exposure of local development server
- **Pages**: Static + Functions (coming soon)

### 4. `install_dependencies`

Installs project dependencies using Poetry.

**Parameters:**
- `project_path`: Path to the FastAPI project
- `include_dev`: Install development dependencies (default: true)

### 5. `run_local_server`

Provides instructions to start the FastAPI development server.

**Parameters:**
- `project_path`: Path to the FastAPI project
- `port`: Server port (default: 8080)
- `host`: Host to bind to (default: "0.0.0.0")

### 6. `get_project_status`

Checks what's configured and what's missing in the project.

**Parameters:**
- `project_path`: Path to the FastAPI project

## Example Workflows

### Complete Project Setup

```python
from fastapi_cloudflare_agent import FastAPICloudflareAgent

agent = FastAPICloudflareAgent()

# Single conversation that does everything
response = agent.chat("""
I want to create a FastAPI project called "Image Classifier API" 
for deploying an image classification model. Please:
1. Generate the project
2. Set up MCP server support
3. Configure it for Cloudflare Tunnel deployment
4. Show me the status
""")

print(response)
```

### Step-by-Step Interaction

```python
agent = FastAPICloudflareAgent()

# Step 1: Generate project
agent.chat("Create a project called 'Sentiment API' for text sentiment analysis")

# Step 2: Add MCP support
agent.chat("Add MCP server support with the name 'sentiment-mcp'")

# Step 3: Configure deployment
agent.chat("Set up Cloudflare Workers deployment")

# Step 4: Check status
agent.chat("What's the current status of the project?")
```

## MCP Server Integration

The agent sets up your FastAPI project as an MCP server that Claude Desktop can connect to:

1. **SSE Endpoint**: `/mcp/sse` - Server-Sent Events endpoint for real-time communication
2. **Tools Endpoint**: `/mcp/tools` - Lists available tools (prediction endpoints, etc.)
3. **Claude Desktop Config**: Auto-generated configuration file

### Using with Claude Desktop

After the agent sets up MCP support:

1. Start your FastAPI server:
   ```bash
   cd your-project
   make run
   ```

2. (Optional) Expose via Cloudflare Tunnel:
   ```bash
   cloudflared tunnel --url http://localhost:8080
   ```

3. Add the configuration to Claude Desktop:
   - Open Claude Desktop settings
   - Go to "Developer" → "Edit Config"
   - Add the contents of `claude_desktop_config.json`

4. Restart Claude Desktop - your FastAPI endpoints are now available as tools!

## Cloudflare Deployment

### Cloudflare Tunnel (Local Development)

Best for development and testing:

```bash
# The agent creates cloudflared.yml configuration
# Then run:
cloudflared tunnel --url http://localhost:8080
```

### Cloudflare Workers (Production)

Serverless deployment:

```bash
# The agent creates wrangler.toml configuration
# Then run:
wrangler login
wrangler deploy
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Cloudflare Agent                  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │            Claude Opus 4.8 with Tool Use               │ │
│  │                                                         │ │
│  │  • Adaptive Thinking for complex reasoning             │ │
│  │  • Natural language interaction                        │ │
│  │  • Stateful conversation history                       │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│                            ▼                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                       Tools                             │ │
│  │                                                         │ │
│  │  [generate] → Cookiecutter Template                    │ │
│  │  [setup_mcp] → Add MCP endpoints                       │ │
│  │  [configure] → Cloudflare deployment                   │ │
│  │  [install] → Poetry dependencies                       │ │
│  │  [status] → Project health check                       │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
        ┌──────────────────────────────────────────┐
        │       Generated FastAPI Project          │
        │                                          │
        │  • ML Model API                          │
        │  • MCP Server Endpoints                  │
        │  • Cloudflare Configuration              │
        │  • Docker Support                        │
        └──────────────────────────────────────────┘
```

## Key Technologies

- **Claude API**: Anthropic's Messages API with tool use
- **Adaptive Thinking**: Claude Opus 4.8's extended thinking capability
- **MCP (Model Context Protocol)**: Standardized protocol for AI tool integration
- **FastAPI**: Modern, fast web framework for building APIs
- **Cloudflare**: Edge deployment and secure tunneling
- **Cookiecutter**: Project templating system

## Advanced Usage

### Custom Tool Execution

You can extend the agent with custom tools:

```python
class CustomAgent(FastAPICloudflareAgent):
    def get_tools(self):
        tools = super().get_tools()
        tools.append({
            "type": "custom",
            "name": "my_custom_tool",
            "description": "Does something custom",
            "input_schema": {
                "type": "object",
                "properties": {
                    "param": {"type": "string"}
                }
            }
        })
        return tools
    
    def execute_tool(self, tool_name, tool_input):
        if tool_name == "my_custom_tool":
            return {"result": "custom action"}
        return super().execute_tool(tool_name, tool_input)
```

### Conversation History

The agent maintains conversation history for context:

```python
agent = FastAPICloudflareAgent()
agent.chat("Create a project")
agent.chat("What project did I just create?")  # Agent remembers!

# Access conversation history
print(agent.conversation_history)

# Access project context
print(agent.project_context)  # Contains project_path, etc.
```

## Troubleshooting

### API Key Issues

```bash
# Make sure your API key is set
echo $ANTHROPIC_API_KEY

# If not set:
export ANTHROPIC_API_KEY="your-key-here"
```

### Cookiecutter Not Found

```bash
pip install cookiecutter
```

### Poetry Issues

```bash
# Install poetry
curl -sSL https://install.python-poetry.org | python3 -

# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"
```

### Cloudflare CLI

```bash
# Install wrangler
npm install -g wrangler

# Install cloudflared
# macOS:
brew install cloudflared

# Linux:
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
```

## Examples

See the `examples/` directory for complete examples:

- `examples/basic_usage.py` - Simple project generation
- `examples/full_workflow.py` - Complete setup with MCP and deployment
- `examples/custom_agent.py` - Extending the agent with custom tools

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Resources

- [Claude API Documentation](https://docs.anthropic.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Cloudflare Workers](https://developers.cloudflare.com/workers/)
- [Cloudflare Tunnels](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)

## Support

For issues and questions:
- GitHub Issues: https://github.com/arthurhenrique/cookiecutter-fastapi/issues
- Claude API Discord: https://discord.gg/anthropic

---

Made with ❤️ using Claude Opus 4.8 and the Claude API
