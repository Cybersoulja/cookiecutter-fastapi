{% raw %}# MCP Server Security Guide

## Overview

This guide covers security best practices for running an MCP server exposed via Cloudflare Tunnels.

## Security Layers

```
┌─────────────────────────────────────────────────┐
│ Layer 1: Cloudflare Edge Security              │
│  - DDoS Protection                              │
│  - WAF Rules                                    │
│  - Rate Limiting                                │
│  - Zero Trust Access                            │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│ Layer 2: Tunnel Security                        │
│  - Encrypted tunnel (TLS)                       │
│  - Service tokens                               │
│  - Certificate authentication                   │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│ Layer 3: Application Security                   │
│  - API key authentication                       │
│  - Request validation                           │
│  - Input sanitization                           │
│  - CORS policies                                │
└─────────────────────────────────────────────────┘
```

## 1. Cloudflare Zero Trust Access

### Setup Access Policy

**Step 1: Create Service Token**

```bash
# Login to Cloudflare
cloudflared tunnel login

# Create service token for MCP server
# (This is done via Cloudflare Dashboard)
```

**Step 2: Configure Access Application**

In Cloudflare Dashboard:

1. Navigate to **Zero Trust** → **Access** → **Applications**
2. Click **Add an Application**
3. Select **Self-hosted**
4. Configure:
   - **Application name**: {{ cookiecutter.project_name }} MCP
   - **Session duration**: 24 hours
   - **Application domain**: `mcp.yourdomain.com`
   - **Path**: `{{ cookiecutter.mcp_endpoint }}`

**Step 3: Add Authentication Method**

Choose one or more:

- **Service Token**: For machine-to-machine communication
- **OAuth**: For user authentication (Google, GitHub, etc.)
- **API Token**: For programmatic access

**Step 4: Create Access Policy**

```
Policy name: Allow MCP Clients
Action: Allow
Include: Service Auth (use your service token)
```

### Using Service Tokens

Generate a service token and configure your MCP client:

```bash
# Client ID and Secret from Cloudflare Dashboard
export CF_SERVICE_TOKEN_ID="your-client-id"
export CF_SERVICE_TOKEN_SECRET="your-client-secret"
```

Client configuration:

```json
{
  "mcpServers": {
    "{{ cookiecutter.project_slug }}": {
      "url": "https://mcp.yourdomain.com{{ cookiecutter.mcp_endpoint }}",
      "headers": {
        "CF-Access-Client-Id": "${CF_SERVICE_TOKEN_ID}",
        "CF-Access-Client-Secret": "${CF_SERVICE_TOKEN_SECRET}",
        "Authorization": "Bearer ${MCP_API_KEY}"
      }
    }
  }
}
```

## 2. API Key Authentication

### Generate Secure API Keys

```python
import secrets

# Generate a secure random API key
api_key = secrets.token_urlsafe(32)
print(f"MCP_API_KEY={api_key}")
```

### Configure API Key

Add to `.env`:

```env
MCP_API_KEY=your-generated-secure-key-here
```

### Implement API Key Validation

Update `app/mcp_main.py`:

```python
from fastapi import Header, HTTPException

async def verify_api_key(authorization: str = Header(None)):
    """Verify API key from Authorization header."""
    expected_key = os.getenv("MCP_API_KEY")
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid auth scheme")
        
        if token != expected_key:
            raise HTTPException(status_code=401, detail="Invalid API key")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization format")

# Add dependency to endpoints
@app.get("{{ cookiecutter.mcp_endpoint }}")
async def handle_mcp(request: Request, _: None = Depends(verify_api_key)):
    # ... MCP handler
```

## 3. Cloudflare WAF Configuration

### Custom WAF Rule: Allow MCP Clients

**Expression:**

```
(http.request.uri.path eq "{{ cookiecutter.mcp_endpoint }}") and 
(
  cf.threat_score lt 10 and
  (http.user_agent contains "python-httpx" or 
   http.user_agent contains "Claude" or
   http.user_agent contains "MCP-Client")
)
```

**Action**: Allow

### Custom WAF Rule: Block Suspicious Traffic

**Expression:**

```
(http.request.uri.path eq "{{ cookiecutter.mcp_endpoint }}") and
(
  cf.threat_score gt 50 or
  cf.bot_management.score lt 30
)
```

**Action**: Block

### Skip Challenge for Legitimate Clients

**Expression:**

```
(http.request.uri.path eq "{{ cookiecutter.mcp_endpoint }}") and
(http.request.headers["cf-access-authenticated-user-email"] ne "")
```

**Action**: Skip → Managed Challenge

## 4. Rate Limiting

### Cloudflare Rate Limiting

**Dashboard Configuration:**

1. **Security** → **WAF** → **Rate limiting rules**
2. **Create rule**:
   - **Rule name**: MCP Endpoint Limit
   - **If incoming requests match**:
     ```
     (http.request.uri.path eq "{{ cookiecutter.mcp_endpoint }}")
     ```
   - **Characteristics**: IP Address
   - **Requests**: 100 per 1 minute
   - **Action**: Block
   - **Duration**: 1 hour

### Application-Level Rate Limiting

Install dependencies:

```bash
poetry add slowapi
```

Implement in `app/mcp_main.py`:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("{{ cookiecutter.mcp_endpoint }}")
@limiter.limit("60/minute")
async def handle_mcp(request: Request):
    # ... MCP handler
```

## 5. CORS Configuration

### Strict CORS Policy

Update `app/mcp_main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

# Production origins only
ALLOWED_ORIGINS = [
    "https://api.anthropic.com",
    "https://claude.ai",
    # Add your specific domains
    "https://your-app.example.com",
]

# Development: add localhost
if DEBUG:
    ALLOWED_ORIGINS.extend([
        "http://localhost:3000",
        "http://localhost:8000",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "CF-Access-Client-Id", "CF-Access-Client-Secret"],
    max_age=600,  # Cache preflight for 10 minutes
)
```

## 6. Input Validation & Sanitization

### Validate Tool Arguments

```python
from pydantic import BaseModel, Field, validator

class PredictInput(BaseModel):
    features: List[float] = Field(..., min_items=1, max_items=1000)
    
    @validator('features')
    def validate_features(cls, v):
        # Check for NaN or Inf
        if any(not math.isfinite(x) for x in v):
            raise ValueError("Features must be finite numbers")
        return v

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any] | None):
    if name == "predict":
        # Validate input
        try:
            validated = PredictInput(**arguments)
            return await handle_predict(validated.dict())
        except ValidationError as e:
            return [types.TextContent(
                type="text",
                text=f"Validation error: {e}"
            )]
```

## 7. Logging & Monitoring

### Enable Comprehensive Logging

```python
from loguru import logger
import sys

# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="INFO" if not DEBUG else "DEBUG",
)

logger.add(
    "logs/mcp_server_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    compression="zip",
    level="INFO",
)

# Log all MCP requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"MCP Request: {request.method} {request.url.path} from {request.client.host}")
    response = await call_next(request)
    logger.info(f"MCP Response: {response.status_code}")
    return response
```

### Monitor with Cloudflare Analytics

1. **Zero Trust Dashboard** → **Access** → **Audit Logs**
2. **Traffic** → **Analytics** → Filter by MCP endpoint
3. Set up **Log Push** to external SIEM

## 8. Secrets Management

### Never Commit Secrets

Add to `.gitignore`:

```
.env
.env.local
*.key
*.pem
cloudflared/*.json
```

### Use Environment Variables

```python
import os
from functools import lru_cache

@lru_cache()
def get_settings():
    """Load settings from environment."""
    return {
        "mcp_api_key": os.getenv("MCP_API_KEY"),
        "allowed_origins": os.getenv("MCP_ALLOWED_ORIGINS", "").split(","),
    }
```

### Rotate API Keys Regularly

```bash
# Generate new key
new_key=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Update .env
echo "MCP_API_KEY=$new_key" >> .env

# Restart server
make run-mcp
```

## 9. Network Security

### Firewall Rules

If running on a VPS:

```bash
# Allow only Cloudflare IPs
ufw allow from 173.245.48.0/20 to any port 8000
ufw allow from 103.21.244.0/22 to any port 8000
# ... add all Cloudflare IP ranges

# Deny all other traffic to port 8000
ufw deny 8000
```

### Disable Direct Port Access

Ensure your server only accepts connections from Cloudflare Tunnel:

```python
# In mcp_main.py
if __name__ == "__main__":
    uvicorn.run(
        "mcp_main:app",
        host="127.0.0.1",  # Only listen on localhost
        port=8000,
    )
```

## 10. Regular Security Audits

### Weekly Checks

- [ ] Review Cloudflare Analytics for unusual traffic
- [ ] Check Access logs for failed auth attempts
- [ ] Verify API keys haven't been exposed
- [ ] Review application logs for errors

### Monthly Tasks

- [ ] Rotate API keys
- [ ] Update dependencies (`poetry update`)
- [ ] Review and update WAF rules
- [ ] Check for security advisories

### Security Scanning

```bash
# Scan for vulnerabilities
poetry run safety check

# Check for outdated packages
poetry show --outdated

# Run security linters
poetry run bandit -r app/
```

## 11. Incident Response

### If API Key is Compromised

1. **Immediately rotate the key**:
   ```bash
   python3 -c "import secrets; print(f'MCP_API_KEY={secrets.token_urlsafe(32)}')" >> .env
   ```

2. **Restart the server**:
   ```bash
   make run-mcp
   ```

3. **Review logs** for unauthorized access
4. **Update all clients** with new key
5. **Monitor** for continued suspicious activity

### If Server is Compromised

1. **Disable Cloudflare Tunnel**:
   ```bash
   cloudflared tunnel delete {{ cookiecutter.project_slug }}-mcp
   ```

2. **Investigate** the breach
3. **Rebuild** server from clean state
4. **Rotate all secrets**
5. **Re-enable** with hardened configuration

## 12. Compliance Considerations

### GDPR / Privacy

- Don't log sensitive user data
- Implement data retention policies
- Provide audit trail capabilities

### SOC 2 / ISO 27001

- Document security controls
- Implement access reviews
- Maintain incident response procedures

## Resources

- [Cloudflare Zero Trust Docs](https://developers.cloudflare.com/cloudflare-one/)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

## Security Disclosure

To report a security vulnerability: security@yourdomain.com{% endraw %}
