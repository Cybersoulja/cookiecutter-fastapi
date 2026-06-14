#!/usr/bin/env python3
"""
Custom agent example - extending the FastAPI Cloudflare Agent.

This example shows how to:
1. Extend the agent with custom tools
2. Override tool execution
3. Add custom logic
"""

import os
import sys
from typing import Any, Dict, List

# Add parent directory to path to import the agent
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi_cloudflare_agent import FastAPICloudflareAgent
from anthropic.types.beta.beta_tool import BetaToolUnion


class CustomFastAPIAgent(FastAPICloudflareAgent):
    """Extended agent with custom tools."""

    def get_tools(self) -> List[BetaToolUnion]:
        """Add custom tools to the base tools."""
        tools = super().get_tools()

        # Add a custom tool for generating Docker Compose configuration
        tools.append({
            "type": "custom",
            "name": "generate_docker_compose",
            "description": "Generate a docker-compose.yml file for the project with FastAPI, PostgreSQL, and Redis services.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to the FastAPI project"
                    },
                    "include_postgres": {
                        "type": "boolean",
                        "description": "Include PostgreSQL database service",
                        "default": True
                    },
                    "include_redis": {
                        "type": "boolean",
                        "description": "Include Redis cache service",
                        "default": True
                    }
                },
                "required": ["project_path"]
            }
        })

        # Add a custom tool for generating test data
        tools.append({
            "type": "custom",
            "name": "generate_test_data",
            "description": "Generate sample test data for the ML model prediction endpoint.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to the FastAPI project"
                    },
                    "num_samples": {
                        "type": "integer",
                        "description": "Number of test samples to generate",
                        "default": 10
                    }
                },
                "required": ["project_path"]
            }
        })

        return tools

    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute custom tools or delegate to parent."""
        if tool_name == "generate_docker_compose":
            return self._generate_docker_compose(tool_input)
        elif tool_name == "generate_test_data":
            return self._generate_test_data(tool_input)
        else:
            return super().execute_tool(tool_name, tool_input)

    def _generate_docker_compose(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate docker-compose.yml configuration."""
        from pathlib import Path

        project_path = Path(params["project_path"])
        include_postgres = params.get("include_postgres", True)
        include_redis = params.get("include_redis", True)

        if not project_path.exists():
            return {"success": False, "error": f"Project path {project_path} does not exist"}

        # Build docker-compose configuration
        compose_content = """version: '3.8'

services:
  fastapi:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DEBUG=False
      - MODEL_PATH=/app/ml/model/
      - MODEL_NAME=model.pkl
"""

        if include_postgres:
            compose_content += """      - DATABASE_URL=postgresql://postgres:password@postgres:5432/fastapi_db
    depends_on:
      - postgres
"""

        if include_redis:
            compose_content += """      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
"""

        compose_content += """    volumes:
      - ./ml/model:/app/ml/model
    command: uvicorn main:app --host 0.0.0.0 --port 8080
"""

        if include_postgres:
            compose_content += """
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=fastapi_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
"""

        if include_redis:
            compose_content += """
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
"""

        if include_postgres or include_redis:
            compose_content += """
volumes:
"""
            if include_postgres:
                compose_content += """  postgres_data:
"""
            if include_redis:
                compose_content += """  redis_data:
"""

        # Write the file
        compose_path = project_path / "docker-compose.yml"
        compose_path.write_text(compose_content)

        return {
            "success": True,
            "message": "Docker Compose configuration generated successfully",
            "file_path": str(compose_path),
            "services": {
                "fastapi": True,
                "postgres": include_postgres,
                "redis": include_redis
            },
            "next_steps": [
                "Review docker-compose.yml configuration",
                "Run: docker-compose up -d",
                "Access API at http://localhost:8080"
            ]
        }

    def _generate_test_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sample test data for ML predictions."""
        import json
        from pathlib import Path

        project_path = Path(params["project_path"])
        num_samples = params.get("num_samples", 10)

        if not project_path.exists():
            return {"success": False, "error": f"Project path {project_path} does not exist"}

        # Generate sample test data
        test_data = []
        for i in range(num_samples):
            test_data.append({
                "id": i + 1,
                "features": {
                    "feature_1": round(i * 1.5, 2),
                    "feature_2": round(i * 2.3, 2),
                    "feature_3": round(i * 0.8, 2)
                }
            })

        # Create tests/data directory
        test_data_dir = project_path / "tests" / "data"
        test_data_dir.mkdir(parents=True, exist_ok=True)

        # Write test data file
        test_data_path = test_data_dir / "sample_predictions.json"
        test_data_path.write_text(json.dumps(test_data, indent=2))

        # Also create an example request file
        example_request = {
            "features": {
                "feature_1": 1.5,
                "feature_2": 2.3,
                "feature_3": 0.8
            }
        }
        example_path = test_data_dir / "example_request.json"
        example_path.write_text(json.dumps(example_request, indent=2))

        return {
            "success": True,
            "message": f"Generated {num_samples} test samples",
            "files": {
                "test_data": str(test_data_path),
                "example_request": str(example_path)
            },
            "next_steps": [
                f"Use test data from {test_data_path} for API testing",
                f"Send example request: curl -X POST http://localhost:8080/api/v1/predict -H 'Content-Type: application/json' -d @{example_path}"
            ]
        }


def main():
    """Run the custom agent example."""
    print("=" * 60)
    print("FastAPI Cloudflare Agent - Custom Extension Example")
    print("=" * 60)
    print()

    # Initialize the custom agent
    agent = CustomFastAPIAgent()

    # Generate a project first
    print("Creating a FastAPI project with custom tools...")
    response = agent.chat("""
    Create a new FastAPI project called "Custom ML API" for machine learning predictions.
    Author: Custom Developer, email: dev@custom.com, output directory: /tmp
    """)
    print(f"\n{response}\n")

    # Use the custom Docker Compose tool
    print("\n" + "-" * 60)
    print("Using custom tool to generate Docker Compose configuration...")
    response = agent.chat("""
    Generate a docker-compose.yml file for the project we just created.
    Include both PostgreSQL and Redis services.
    """)
    print(f"\n{response}\n")

    # Use the custom test data generation tool
    print("\n" + "-" * 60)
    print("Using custom tool to generate test data...")
    response = agent.chat("""
    Generate 20 sample test data entries for the prediction endpoint
    in the project we created.
    """)
    print(f"\n{response}\n")

    print("\n" + "=" * 60)
    print("Custom agent example complete!")
    print("This shows how you can extend the base agent with your own tools.")
    print("=" * 60)


if __name__ == "__main__":
    main()
