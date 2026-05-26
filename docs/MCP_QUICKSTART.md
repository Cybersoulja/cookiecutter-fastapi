# MCP Server Quick Start Guide

## 5-Minute Setup

This guide gets you up and running with the MCP server in minutes.

### Prerequisites

```bash
# Install cookiecutter
pip install cookiecutter

# Install cloudflared (macOS)
brew install cloudflared

# Or Linux
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
```

### Step 1: Generate Project

```bash
cookiecutter gh:arthurhenrique/cookiecutter-fastapi
```

Answer the prompts:
- `enable_mcp_server`: **yes**
- Other fields: fill as desired

### Step 2: Install & Run

```bash
cd your-project-name

# Install dependencies
make install-mcp

# Run MCP server
make run-mcp
```

Server starts at: `http://localhost:8000/mcp`

### Step 3: Create Tunnel

In a new terminal:

```bash
# Quick temporary tunnel
make tunnel-dev
```

You'll get a URL like: `https://random-name.trycloudflare.com`

### Step 4: Test It

```bash
# Test locally
curl http://localhost:8000/health

# Test via tunnel
curl https://random-name.trycloudflare.com/health

# Test MCP endpoint
curl https://random-name.trycloudflare.com/mcp
```

### Step 5: Configure AI Client

Copy your tunnel URL and create client config:

```json
{
  "mcpServers": {
    "my-fastapi": {
      "url": "https://random-name.trycloudflare.com/mcp",
      "transport": "sse"
    }
  }
}
```

## Next Steps

### Production Setup

1. **Create named tunnel:**
   ```bash
   cloudflared tunnel login
   cloudflared tunnel create my-mcp-tunnel
   cloudflared tunnel route dns my-mcp-tunnel mcp.yourdomain.com
   ```

2. **Configure security:**
   - Generate API key: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`
   - Add to `.env`: `MCP_API_KEY=your-generated-key`
   - Set up Cloudflare Access (see docs/MCP_SECURITY.md)

3. **Deploy:**
   ```bash
   # Docker
   docker-compose -f docker-compose.mcp.yml up -d

   # Or systemd
   sudo cp deployment/mcp-server.service.example /etc/systemd/system/my-mcp.service
   sudo systemctl enable my-mcp
   sudo systemctl start my-mcp
   ```

## Common Commands

```bash
# Development
make run-mcp              # Start MCP server
make tunnel-dev           # Quick tunnel
make test-mcp            # Test endpoint

# Production
make run-mcp-prod        # Production server
make tunnel-info         # Tunnel status

# Help
make mcp-help            # Show all MCP commands
```

## Troubleshooting

**Server won't start?**
```bash
# Check dependencies
poetry install --with mcp

# Check port availability
lsof -i :8000
```

**Tunnel not working?**
```bash
# Check cloudflared
cloudflared --version

# Restart tunnel
pkill cloudflared
make tunnel-dev
```

**Can't connect to MCP?**
```bash
# Check logs
tail -f logs/app.log

# Test locally first
curl http://localhost:8000/mcp
```

## Example: Make a Prediction

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "predict",
      "arguments": {
        "features": [1.5, 2.3, 4.1, 0.8]
      }
    },
    "id": 1
  }'
```

## Full Documentation

- [Complete Setup Guide](./MCP_CLOUDFLARE_SETUP.md)
- [Security Best Practices](./MCP_SECURITY.md)
- Configuration examples in project root
- Python client: `examples/mcp_client_example.py`

## Need Help?

- Check the [main documentation](./MCP_CLOUDFLARE_SETUP.md)
- Review [security guide](./MCP_SECURITY.md)
- Open an issue on GitHub

---

**You're ready!** Your FastAPI app is now accessible to AI agents via MCP. 🚀
