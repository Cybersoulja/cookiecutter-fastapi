# MCP Server with Cloudflare Tunnel Setup

## Overview

This guide explains how to expose your FastAPI application as an **MCP (Model Context Protocol) server** accessible to remote AI clients using **Cloudflare Tunnels**. This allows AI assistants like Claude to securely invoke your API endpoints and ML models remotely.

## What is MCP?

**Model Context Protocol (MCP)** is a standardized protocol that enables AI assistants to interact with external tools and services. By exposing your FastAPI app as an MCP server, you enable:

- Remote AI clients to invoke your ML prediction endpoints
- Secure tool execution through Cloudflare's infrastructure
- No exposed ports on your local machine
- Production-ready integration with Claude Managed Agents

## Architecture Overview

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│  Claude Agent   │◄────────┤ Cloudflare Tunnel│◄────────┤  Local FastAPI  │
│   (Remote)      │  HTTPS  │   (Secure Edge)  │  Local  │   + MCP Server  │
└─────────────────┘         └──────────────────┘         └─────────────────┘
```

## Prerequisites

- Python 3.9+ with Poetry
- Cloudflare account (free tier works)
- `cloudflared` CLI installed
- Your FastAPI project generated from this cookiecutter template

### Install Cloudflared

**macOS:**
```bash
brew install cloudflared
```

**Linux:**
```bash
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
```

**Windows:**
```powershell
winget install --id Cloudflare.cloudflared
```

## Quick Start (Development)

### 1. Generate Project with MCP Support

When creating your project, enable MCP support:

```bash
cookiecutter gh:arthurhenrique/cookiecutter-fastapi
```

Select `yes` when prompted for `enable_mcp_server`.

### 2. Install Dependencies

```bash
cd your-project-name
poetry install --with mcp
```

### 3. Run the MCP Server Locally

```bash
poetry run uvicorn app.mcp_main:app --host 0.0.0.0 --port 8000
```

### 4. Create Temporary Tunnel

```bash
cloudflared tunnel --url http://localhost:8000
```

This provides a temporary URL like `https://random-name.trycloudflare.com`.

### 5. Test the MCP Endpoint

```bash
curl https://random-name.trycloudflare.com/mcp
```

## Production Setup

### Step 1: Create a Named Tunnel

```bash
# Login to Cloudflare
cloudflared tunnel login

# Create a tunnel
cloudflared tunnel create my-mcp-tunnel

# Note the tunnel UUID from the output
```

### Step 2: Configure DNS

```bash
# Route your domain to the tunnel
cloudflared tunnel route dns my-mcp-tunnel mcp.yourdomain.com
```

### Step 3: Create Tunnel Configuration

Create `~/.cloudflared/config.yml`:

```yaml
tunnel: <YOUR_TUNNEL_UUID>
credentials-file: /path/to/.cloudflared/<TUNNEL_UUID>.json

ingress:
  # Route to MCP server
  - hostname: mcp.yourdomain.com
    service: http://localhost:8000
    
  # Catch-all rule (required)
  - service: http_status:404

# Optional: Enable logging
loglevel: info
```

### Step 4: Run the Tunnel as a Service

**Linux (systemd):**
```bash
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

**macOS (launchd):**
```bash
sudo cloudflared service install
sudo launchctl start cloudflared
```

**Docker:**
```bash
docker run -d \
  --name cloudflared \
  --restart unless-stopped \
  -v ~/.cloudflared:/etc/cloudflared \
  cloudflare/cloudflared:latest \
  tunnel --config /etc/cloudflared/config.yml run
```

### Step 5: Start Your MCP Server

```bash
# Development
make run-mcp

# Production (with process manager)
poetry run gunicorn app.mcp_main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## MCP Server Configuration

### Environment Variables

Add to your `.env` file:

```env
# MCP Configuration
MCP_SERVER_NAME=your-project-mcp
MCP_SERVER_VERSION=1.0.0
MCP_ENDPOINT=/mcp

# Security
MCP_API_KEY=your-secret-api-key
MCP_ALLOWED_ORIGINS=https://api.anthropic.com,https://claude.ai

# Model Configuration (if exposing ML tools)
MODEL_PATH=./ml/model/
MODEL_NAME=model.pkl
```

### Available MCP Tools

When MCP is enabled, your server exposes these tools to AI clients:

#### 1. `predict`
Execute ML model predictions.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "features": {
      "type": "array",
      "description": "Feature vector for prediction"
    }
  },
  "required": ["features"]
}
```

**Example:**
```json
{
  "features": [1.5, 2.3, 4.1, 0.8]
}
```

#### 2. `health_check`
Check server and model health status.

**Output:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0"
}
```

#### 3. `get_model_info`
Get information about the loaded ML model.

**Output:**
```json
{
  "model_name": "model.pkl",
  "model_path": "./ml/model/",
  "feature_count": 10,
  "model_type": "sklearn.ensemble.RandomForestClassifier"
}
```

## Remote Client Configuration

### For Claude Managed Agents

Configure your remote MCP client with:

```json
{
  "mcpServers": {
    "your-fastapi-mcp": {
      "url": "https://mcp.yourdomain.com/mcp",
      "transport": "sse",
      "env": {
        "MCP_API_KEY": "your-secret-api-key"
      }
    }
  }
}
```

### For Custom Python Clients

```python
import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def main():
    async with sse_client("https://mcp.yourdomain.com/mcp") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Call predict tool
            result = await session.call_tool("predict", {
                "features": [1.5, 2.3, 4.1, 0.8]
            })
            print(result)

asyncio.run(main())
```

## Security Best Practices

### 1. Enable Cloudflare Access

Protect your tunnel with Zero Trust authentication:

```bash
# Create a service token
cloudflared tunnel token create my-mcp-tunnel

# Or use Cloudflare Access for OAuth
```

In Cloudflare Dashboard:
1. Go to Zero Trust → Access → Applications
2. Create new Application
3. Set domain: `mcp.yourdomain.com`
4. Add authentication method (OAuth, service token, etc.)

### 2. API Key Authentication

The template includes bearer token authentication. Set in `.env`:

```env
MCP_API_KEY=your-very-secret-key-change-this
```

Clients must include:
```
Authorization: Bearer your-very-secret-key-change-this
```

### 3. Cloudflare WAF Rules

If AI clients are blocked by security challenges:

**Create WAF Custom Rule:**
1. Cloudflare Dashboard → Security → WAF
2. Create Custom Rule
3. Rule name: "Allow MCP Endpoint"
4. Expression:
   ```
   (http.request.uri.path contains "/mcp") and 
   (http.user_agent contains "python-httpx" or http.user_agent contains "Claude")
   ```
5. Action: Skip → All remaining custom rules, Managed rules

### 4. Rate Limiting

Add rate limiting to prevent abuse:

**Cloudflare Dashboard:**
1. Security → WAF → Rate limiting rules
2. Create rule for `/mcp` endpoint
3. Set threshold (e.g., 100 requests per minute)

**Application Level (in code):**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/mcp")
@limiter.limit("60/minute")
async def mcp_endpoint(request: Request):
    # MCP handler
    pass
```

### 5. CORS Configuration

Update `app/mcp_server.py` allowed origins:

```python
ALLOWED_ORIGINS = [
    "https://api.anthropic.com",
    "https://claude.ai",
    "https://your-custom-domain.com"
]
```

## Monitoring & Debugging

### Check Tunnel Status

```bash
# List all tunnels
cloudflared tunnel list

# Check tunnel info
cloudflared tunnel info my-mcp-tunnel

# View logs
journalctl -u cloudflared -f  # Linux
tail -f /var/log/cloudflared.log  # macOS
```

### MCP Server Logs

```bash
# Application logs (Loguru)
tail -f logs/app.log

# Uvicorn access logs
poetry run uvicorn app.mcp_main:app --log-level debug
```

### Test MCP Tools Locally

```bash
# Using curl
curl -X POST https://mcp.yourdomain.com/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
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

## Troubleshooting

### Common Issues

**1. Tunnel not connecting:**
```bash
# Check tunnel status
cloudflared tunnel info my-mcp-tunnel

# Restart tunnel
sudo systemctl restart cloudflared
```

**2. 403 Forbidden errors:**
- Check Cloudflare Access rules
- Verify WAF rules aren't blocking requests
- Ensure API key is correct

**3. MCP tools not responding:**
- Verify FastAPI app is running on port 8000
- Check application logs for errors
- Test locally: `curl http://localhost:8000/mcp`

**4. Model loading errors:**
- Ensure `MODEL_PATH` and `MODEL_NAME` are correct
- Verify model file exists and is readable
- Check model compatibility with current scikit-learn version

### Debug Mode

Enable debug logging:

```env
DEBUG=true
LOG_LEVEL=DEBUG
```

## Performance Optimization

### 1. Use Production ASGI Server

```bash
# Gunicorn with Uvicorn workers
poetry run gunicorn app.mcp_main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  -b 0.0.0.0:8000 \
  --timeout 120
```

### 2. Enable HTTP/2 in Cloudflare

HTTP/2 is automatically enabled for HTTPS tunnels.

### 3. Caching

Configure Cloudflare caching rules for static responses.

### 4. Connection Pooling

Cloudflare Tunnels maintain persistent connections, reducing latency.

## Cost Considerations

**Cloudflare Tunnel:** FREE
- Unlimited bandwidth
- Unlimited requests
- No egress fees

**Cloudflare Zero Trust:** 
- Free tier: 50 users
- Paid: $7/user/month for advanced features

**Compute:**
- Your local machine or cloud VM
- Estimate: ~$5-20/month for small cloud instance

## Advanced Topics

### Multi-Region Deployment

Deploy multiple tunnel endpoints for redundancy:

```yaml
# config-us.yml
tunnel: tunnel-us-uuid
ingress:
  - hostname: mcp-us.yourdomain.com
    service: http://localhost:8000

# config-eu.yml  
tunnel: tunnel-eu-uuid
ingress:
  - hostname: mcp-eu.yourdomain.com
    service: http://localhost:8000
```

### Load Balancing

Use Cloudflare Load Balancer to distribute across regions:

1. Create multiple tunnel endpoints
2. Cloudflare Dashboard → Traffic → Load Balancing
3. Add origins (your tunnel endpoints)
4. Configure health checks

### Custom MCP Tools

Add custom tools by editing `app/mcp_server.py`:

```python
@server.tool()
async def custom_tool(argument: str) -> str:
    """
    Description of your custom tool.
    
    Args:
        argument: Description of the argument
        
    Returns:
        Result description
    """
    # Your implementation
    return f"Processed: {argument}"
```

## Example Use Cases

### 1. Remote ML Inference
AI agents can invoke your trained models for predictions.

### 2. Data Processing Pipeline
Expose data transformation endpoints as MCP tools.

### 3. Multi-Model Serving
Serve multiple ML models through different MCP tools.

### 4. A/B Testing
Route MCP requests to different model versions.

## Resources

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Cloudflare Tunnel Documentation](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

## Support

For issues specific to:
- **Template:** Open issue at cookiecutter-fastapi repo
- **MCP Protocol:** MCP GitHub issues
- **Cloudflare Tunnels:** Cloudflare Community

## Security Disclosure

If you discover a security vulnerability, please email: security@yourdomain.com
