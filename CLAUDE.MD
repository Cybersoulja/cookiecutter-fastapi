# CLAUDE.MD - Project Context for AI Assistant

## Project Overview

This is **cookiecutter-fastapi**, a Cookiecutter template for generating FastAPI projects with built-in machine learning model serving capabilities. It provides a production-ready boilerplate for building ML-powered APIs.

## Repository Type

This is a **template repository** using Cookiecutter. It is not a runnable application itself, but rather a template that generates FastAPI projects. The actual project structure is in `{{cookiecutter.project_slug}}/` and uses Jinja2 templating syntax.

## Key Concepts

### Cookiecutter Template Variables
- Defined in `cookiecutter.json`
- Variables like `{{cookiecutter.project_name}}`, `{{cookiecutter.project_slug}}` are placeholders
- When users run `cookiecutter gh:arthurhenrique/cookiecutter-fastapi`, these get replaced with user input

### Template Structure
```
cookiecutter-fastapi/                    # Template repository root
├── cookiecutter.json                     # Template configuration
├── {{cookiecutter.project_slug}}/        # Generated project template
│   ├── app/                              # FastAPI application
│   │   ├── api/routes/                   # API endpoints
│   │   ├── core/                         # Config, logging, events
│   │   ├── models/                       # Pydantic models
│   │   └── services/                     # Business logic
│   ├── ml/                               # Machine learning pipeline
│   │   ├── data/                         # Data processing scripts
│   │   ├── features/                     # Feature engineering
│   │   └── model/                        # Model training/prediction
│   ├── tests/                            # Pytest test suite
│   ├── notebooks/                        # Jupyter notebooks
│   └── pyproject.toml                    # Poetry dependencies
```

## Generated Project Features

The template generates projects with:

1. **FastAPI Application**
   - RESTful API structure
   - Swagger/Redocs documentation
   - Pydantic models for validation
   - Custom error handling
   - Structured logging

2. **ML Model Serving**
   - `/predict` endpoint for model inference
   - Configurable model loading
   - Example integration with scikit-learn/pickle models

3. **Development Tools**
   - Poetry for dependency management
   - Makefile for common tasks
   - Pytest for testing
   - Pylint configuration
   - Docker support

4. **Cloud Deployment Ready**
   - GCP Cloud Run deployment scripts
   - AWS Lambda support (main-aws-lambda.py)
   - Docker configuration

## Important Files to Know

### Template Configuration
- `cookiecutter.json` - Template variables and defaults
- `setup.py` - Cookiecutter template installation

### Generated Project Files
- `{{cookiecutter.project_slug}}/app/main.py` - FastAPI app entry point
- `{{cookiecutter.project_slug}}/app/api/routes/predictor.py` - ML prediction endpoint
- `{{cookiecutter.project_slug}}/app/core/config.py` - Application configuration
- `{{cookiecutter.project_slug}}/pyproject.toml` - Poetry dependencies
- `{{cookiecutter.project_slug}}/Makefile` - Development commands

## Development Guidelines

### When Modifying This Template

1. **Template Files**: Changes to files in `{{cookiecutter.project_slug}}/` affect generated projects
2. **Jinja2 Syntax**: Use `{{ }}` for variables, `{% %}` for logic
3. **Test Template**: After changes, test by running cookiecutter locally
4. **Dependencies**: Update `{{cookiecutter.project_slug}}/pyproject.toml` for Python packages

### Common Tasks

#### Adding New Template Variables
1. Add to `cookiecutter.json`
2. Use in templates as `{{cookiecutter.variable_name}}`

#### Updating Dependencies
- Edit `{{cookiecutter.project_slug}}/pyproject.toml`
- Update `{{cookiecutter.project_slug}}/poetry.lock` if testing locally

#### Adding New Routes
- Add to `{{cookiecutter.project_slug}}/app/api/routes/`
- Register in `{{cookiecutter.project_slug}}/app/api/routes/api.py`

#### Modifying ML Pipeline
- Edit files in `{{cookiecutter.project_slug}}/ml/`
- Update predictor logic in `app/api/routes/predictor.py`

### Technology Stack (Generated Projects)

- **Framework**: FastAPI (async Python web framework)
- **Python**: 3.11.0+
- **Package Manager**: Poetry
- **ML Framework**: Configurable (default assumes scikit-learn/pickle)
- **Testing**: Pytest
- **Linting**: Pylint
- **Logging**: Loguru
- **Containerization**: Docker
- **Cloud**: GCP Cloud Run, AWS Lambda

## Architecture Patterns

### Generated Project Architecture

1. **API Layer** (`app/api/`): HTTP routes and request handling
2. **Core Layer** (`app/core/`): Configuration, logging, events
3. **Service Layer** (`app/services/`): Business logic, ML inference
4. **Model Layer** (`app/models/`): Pydantic schemas for validation
5. **ML Pipeline** (`ml/`): Data processing, training, prediction scripts

### Key Design Decisions

- **Separation of Concerns**: API, business logic, and ML code are separated
- **Configuration Management**: Environment variables via `.env` file
- **Async Support**: FastAPI's async capabilities for better performance
- **ML Flexibility**: Template is model-agnostic, easily customizable

## Testing

Generated projects include:
- Test structure in `{{cookiecutter.project_slug}}/tests/`
- Run tests with `make test`
- Pytest configuration included

When modifying the template, consider:
- Adding example tests for new features
- Ensuring generated code is testable

## Deployment

Generated projects support:

### GCP Cloud Run
- Dockerfile included
- Deploy with Cloud Build
- Scripts in template

### AWS Lambda
- `main-aws-lambda.py` for Lambda compatibility
- SAM CLI deployment
- Includes AWS-specific configuration

### Docker
- Standard Dockerfile
- docker-compose.yml for local development
- Can deploy to any container platform

## Environment Variables

Generated projects use:
- `MODEL_PATH`: Path to ML model files
- `MODEL_NAME`: Model filename (e.g., model.pkl)
- Additional variables in `app/core/config.py`

## Common Pitfalls

1. **Don't Run Template Directly**: This is a template, not a runnable app
2. **Jinja2 Syntax**: Files with `{{cookiecutter.*}}` need cookiecutter to process
3. **Testing Changes**: Test template generation after modifications
4. **Dependencies**: Keep poetry.lock in sync with pyproject.toml

## Contributing Guidelines

When contributing to this template:

1. **Test Generation**: Always test cookiecutter generation after changes
2. **Documentation**: Update both root README.md and template README.md
3. **Backwards Compatibility**: Consider existing users of the template
4. **Python Version**: Target specified Python version (currently 3.11.0)
5. **Dependencies**: Justify new dependencies, keep minimal

## Resources

- FastAPI Documentation: https://fastapi.tiangolo.com/
- Cookiecutter Documentation: https://cookiecutter.readthedocs.io/
- Poetry Documentation: https://python-poetry.org/docs/

## Notes for AI Assistants

- This is a **template repository**, not a deployable application
- Files in `{{cookiecutter.project_slug}}/` contain Jinja2 templating
- Changes here affect all future projects generated from this template
- Always consider the impact on generated projects
- Test template generation when making significant changes
- The `_copy_without_render` in cookiecutter.json prevents certain files from being processed
