#!/bin/bash
#
# Quick start script for FastAPI Cloudflare Agent
#
# This script sets up and runs the FastAPI Cookiecutter Agent for Cloudflare
#

set -e

echo "=========================================="
echo "FastAPI Cloudflare Agent - Quick Start"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+ first."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Check if ANTHROPIC_API_KEY is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo ""
    echo "⚠️  ANTHROPIC_API_KEY environment variable is not set."
    echo ""
    echo "Please set your Anthropic API key:"
    echo "  export ANTHROPIC_API_KEY='your-api-key-here'"
    echo ""
    echo "Get an API key at: https://console.anthropic.com/"
    echo ""
    read -p "Enter your Anthropic API key now (or press Enter to skip): " api_key

    if [ -n "$api_key" ]; then
        export ANTHROPIC_API_KEY="$api_key"
        echo "✓ API key set for this session"
    else
        echo "⚠️  Skipping API key setup. Agent will fail without it."
    fi
else
    echo "✓ ANTHROPIC_API_KEY is set"
fi

# Install dependencies
echo ""
echo "Installing agent dependencies..."
pip install -q -r agent_requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Check if cookiecutter is available
if ! command -v cookiecutter &> /dev/null; then
    echo "⚠️  Cookiecutter not found in PATH, but should be installed via requirements"
fi

echo ""
echo "=========================================="
echo "Starting FastAPI Cloudflare Agent..."
echo "=========================================="
echo ""
echo "You can now interact with the agent using natural language."
echo "Examples:"
echo "  - 'Create a FastAPI project for image classification'"
echo "  - 'Set up MCP server support'"
echo "  - 'Configure Cloudflare deployment'"
echo ""
echo "Type 'quit' to exit."
echo ""

# Run the agent
python3 fastapi_cloudflare_agent.py
