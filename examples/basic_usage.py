#!/usr/bin/env python3
"""
Basic usage example for the FastAPI Cloudflare Agent.

This example shows how to:
1. Initialize the agent
2. Generate a FastAPI project
3. Get basic information
"""

import os
import sys

# Add parent directory to path to import the agent
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi_cloudflare_agent import FastAPICloudflareAgent


def main():
    """Run a basic example."""
    print("=" * 60)
    print("FastAPI Cloudflare Agent - Basic Usage Example")
    print("=" * 60)
    print()

    # Initialize the agent
    # Make sure ANTHROPIC_API_KEY is set in environment
    agent = FastAPICloudflareAgent()

    # Simple project generation
    print("Creating a new FastAPI project...")
    response = agent.chat(
        "Create a new FastAPI project called 'Sentiment Analysis API' "
        "for analyzing text sentiment. Author: John Doe, email: john@example.com"
    )
    print(f"\nAgent Response:\n{response}\n")

    # Ask about the project
    print("-" * 60)
    print("Asking about the generated project...")
    response = agent.chat(
        "What files and directories were created in the project?"
    )
    print(f"\nAgent Response:\n{response}\n")

    # Get next steps
    print("-" * 60)
    print("Getting recommendations for next steps...")
    response = agent.chat(
        "What should I do next to get this project running?"
    )
    print(f"\nAgent Response:\n{response}\n")


if __name__ == "__main__":
    main()
