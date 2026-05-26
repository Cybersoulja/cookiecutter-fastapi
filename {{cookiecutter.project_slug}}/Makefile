SHELL := /bin/bash

# Variables definitions
# -----------------------------------------------------------------------------

ifeq ($(TIMEOUT),)
TIMEOUT := 60
endif

ifeq ($(MODEL_PATH),)
MODEL_PATH := {{cookiecutter.machine_learn_model_path}}
endif

ifeq ($(MODEL_NAME),)
MODEL_NAME := {{cookiecutter.machine_learn_model_name}}
endif

# Target section and Global definitions
# -----------------------------------------------------------------------------
.PHONY: all clean test install run deploy down{% if cookiecutter.enable_mcp_server == 'yes' %} install-mcp run-mcp test-mcp tunnel-dev{% endif %}

all: clean test install run deploy down

test:
	poetry run pytest tests -vv --show-capture=all

install: generate_dot_env
	pip install --upgrade pip
	pip install poetry
	poetry install --with dev

run:
	PYTHONPATH=app/ poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8080

deploy: generate_dot_env
	docker-compose build
	docker-compose up -d

down:
	docker-compose down

generate_dot_env:
	@if [[ ! -e .env ]]; then \
		cp .env.example .env; \
	fi

clean:
	@find . -name '*.pyc' -exec rm -rf {} \;
	@find . -name '__pycache__' -exec rm -rf {} \;
	@find . -name 'Thumbs.db' -exec rm -rf {} \;
	@find . -name '*~' -exec rm -rf {} \;
	rm -rf .cache
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	rm -rf htmlcov
	rm -rf .tox/
	rm -rf docs/_build

{% if cookiecutter.enable_mcp_server == 'yes' %}
# MCP Server Targets
# -----------------------------------------------------------------------------

install-mcp:
	@echo "Installing MCP server dependencies..."
	poetry install --with dev,mcp

run-mcp: generate_dot_env
	@echo "Starting MCP Server on http://localhost:8000{{ cookiecutter.mcp_endpoint }}"
	PYTHONPATH=app/ poetry run uvicorn mcp_main:app --reload --host 0.0.0.0 --port 8000

run-mcp-prod: generate_dot_env
	@echo "Starting MCP Server (production mode)..."
	PYTHONPATH=app/ poetry run gunicorn mcp_main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

test-mcp:
	@echo "Testing MCP endpoint..."
	@curl -s http://localhost:8000{{ cookiecutter.mcp_endpoint }} || echo "Server not running. Start with 'make run-mcp'"

tunnel-dev:
	@echo "Starting Cloudflare Tunnel (development mode)..."
	@echo "This will create a temporary public URL for testing"
	@which cloudflared > /dev/null || (echo "Error: cloudflared not installed. See docs/MCP_CLOUDFLARE_SETUP.md" && exit 1)
	cloudflared tunnel --url http://localhost:8000

tunnel-info:
	@echo "Cloudflare Tunnel Information:"
	@cloudflared tunnel list || echo "No tunnels found. Create one with: cloudflared tunnel create my-mcp-tunnel"

mcp-help:
	@echo "MCP Server Commands:"
	@echo "  make install-mcp    - Install MCP dependencies"
	@echo "  make run-mcp        - Run MCP server (development)"
	@echo "  make run-mcp-prod   - Run MCP server (production with gunicorn)"
	@echo "  make test-mcp       - Test MCP endpoint locally"
	@echo "  make tunnel-dev     - Start temporary Cloudflare Tunnel"
	@echo "  make tunnel-info    - Show Cloudflare Tunnel information"
	@echo ""
	@echo "See docs/MCP_CLOUDFLARE_SETUP.md for complete setup guide"
{% endif %}