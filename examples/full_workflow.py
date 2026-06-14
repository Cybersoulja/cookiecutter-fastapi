#!/usr/bin/env python3
"""
Full workflow example for the FastAPI Cloudflare Agent.

This example shows a complete workflow:
1. Generate a FastAPI project
2. Set up MCP server support
3. Configure Cloudflare deployment
4. Check project status
"""

import os
import sys

# Add parent directory to path to import the agent
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi_cloudflare_agent import FastAPICloudflareAgent


def main():
    """Run a full workflow example."""
    print("=" * 60)
    print("FastAPI Cloudflare Agent - Full Workflow Example")
    print("=" * 60)
    print()

    # Initialize the agent
    agent = FastAPICloudflareAgent()

    # Step 1: Generate the project
    print("STEP 1: Generating FastAPI project...")
    print("-" * 60)
    response = agent.chat("""
    Create a new FastAPI project with these details:
    - Project name: "Image Classification API"
    - Description: "REST API for image classification using deep learning"
    - Author: Jane Smith
    - Email: jane.smith@example.com
    - Output directory: /tmp
    """)
    print(f"\n{response}\n")

    # Step 2: Set up MCP server
    print("\nSTEP 2: Setting up MCP server support...")
    print("-" * 60)
    response = agent.chat("""
    Set up MCP server support for the project we just created.
    Use the server name "image-classifier-mcp" and enable Cloudflare Tunnel support.
    """)
    print(f"\n{response}\n")

    # Step 3: Configure Cloudflare deployment
    print("\nSTEP 3: Configuring Cloudflare deployment...")
    print("-" * 60)
    response = agent.chat("""
    Configure the project for Cloudflare Tunnel deployment so I can
    securely expose my local development server.
    """)
    print(f"\n{response}\n")

    # Step 4: Get project status
    print("\nSTEP 4: Checking project status...")
    print("-" * 60)
    response = agent.chat("""
    What's the current status of the project? What's configured and what's missing?
    """)
    print(f"\n{response}\n")

    # Step 5: Get deployment instructions
    print("\nSTEP 5: Getting deployment instructions...")
    print("-" * 60)
    response = agent.chat("""
    How do I deploy this project to production using Cloudflare?
    Give me step-by-step instructions.
    """)
    print(f"\n{response}\n")

    print("\n" + "=" * 60)
    print("Workflow complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
