# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Type

This is **cookiecutter-fastapi**, a [Cookiecutter](https://cookiecutter.readthedocs.io/) template repository — not a runnable application. It generates FastAPI projects with built-in ML model serving. The repo has two distinct layers:

- **Template root** (`cookiecutter.json`, `setup.py`, this file, docs) — metadata for the cookiecutter tool itself.
- **`{{cookiecutter.project_slug}}/`** — the actual project template, written with Jinja2 placeholders (`{{cookiecutter.*}}`). This is what gets copied and rendered into a new project when someone runs `cookiecutter gh:arthurhenrique/cookiecutter-fastapi`. Nearly all substantive code changes belong here.

Because `{{cookiecutter.project_slug}}/` is not itself an importable Python package (its name literally contains `{{ }}`), you cannot run linters/tests against it in place — it must first be rendered by cookiecutter into a real directory.

## Commands

All commands below are run **inside a generated project** (i.e. after `cookiecutter --no-input .` renders `{{cookiecutter.project_slug}}/` into a real folder), using the `Makefile` at that project's root:

```sh
make install   # pip install poetry, then `poetry install --with dev`; also copies .env.example -> .env
make run       # PYTHONPATH=app/ poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8080
make test      # poetry run pytest tests -vv --show-capture=all
make deploy    # docker-compose build && docker-compose up -d
make down      # docker-compose down
make clean     # remove caches/build artifacts
```

To test template changes end-to-end (this mirrors `.github/workflows/ci.yaml`):

```sh
pip install poetry cookiecutter
cookiecutter --no-input .        # renders using cookiecutter.json defaults, output dir e.g. name-of-the-project/
cd name-of-the-project
make install
make test
```

Run a single test (from inside the rendered project directory, where `pytest` sees both `app/` and `tests/` from the project root):

```sh
poetry run pytest tests/test_pagination_behavior.py::test_pagenation_400_10th_page -vv
```

Formatting/linting tools present in the generated project's dependencies: `black` (line-length 88, config in `pyproject.toml`), `pylint` (config in `.pylintrc`), `autopep8`. There are no Makefile targets for these; invoke directly, e.g. `poetry run black app ml tests`.

CI (`.github/workflows/ci.yaml`) only exercises the render-then-test flow above on Python 3.9 — it does not lint the template root itself.

## Architecture (generated project, i.e. inside `{{cookiecutter.project_slug}}/`)

The generated app has two independent halves that only meet at `app/services/predict.py` and `app/api/routes/predictor.py`:

1. **FastAPI service** (`app/`)
   - `main.py` builds the `FastAPI` app, mounts `api_router` under `API_PREFIX` (`/api`), and *optionally* wires an app-startup handler (`pre_load` is hardcoded `False`, so `create_start_app_handler`/model preloading is currently dead code unless enabled). Note this preload path is also currently broken: `core/events.py` calls `MachineLearningModelHandlerScore.get_model()` with no arguments, but `get_model` requires a `load_wrapper` positional arg — flipping `pre_load` to `True` as-is will crash on startup and needs that call fixed first.
   - `api/routes/api.py` is the single place new route modules get registered (`router.include_router(...)`) — mirrors the pattern used for `predictor.py`, mounted at `/v1`.
   - `api/routes/predictor.py` defines the two real endpoints: `POST /predict` and `GET /health`. Both call `get_prediction()`, a thin wrapper the template README explicitly tells users to edit when swapping in a different model type (`load_wrapper`/`method` args to `MachineLearningModelHandlerScore.predict`).
   - `core/config.py` is the single source of runtime config, read via `starlette.config.Config(".env")` — env vars like `MODEL_PATH`, `MODEL_NAME`, `INPUT_EXAMPLE`, `DEBUG`, `SECRET_KEY`, `PROJECT_NAME` all flow through here. It also configures loguru/stdlib logging interop at import time via `core/logging.py`'s `InterceptHandler`.
   - `core/paginator.py` provides a generic, framework-agnostic `pagenation()` helper (note the intentional/legacy misspelling) used for building paged listing responses; it is the one piece of the template with a real unit test (`tests/test_pagination_behavior.py`).
   - `core/errors.py` defines `PredictException`/`ModelLoadException`, raised from `services/predict.py`.
   - `models/prediction.py` holds the Pydantic v2 schemas (`MachineLearningDataInput`, `MachineLearningResponse`, `HealthResponse`). `MachineLearningDataInput` is hardcoded to 5 floats (`feature1..5`) purely as an example — real usage requires editing this schema to match the actual model's input.

2. **ML pipeline** (`ml/`) — independent of the API at import time; only its *output artifact* (a pickled model file) is consumed by the API via `services/predict.py`.
   - `ml/data/make_dataset.py`, `ml/features/build_features.py` — placeholder scripts for the data → features pipeline.
   - `ml/model/` — where the model file lives (`MODEL_PATH`/`MODEL_NAME` from config), plus `examples/example.json`, the fixture used by the `/health` endpoint to sanity-check the model at request time.
   - `services/predict.py`'s `MachineLearningModelHandlerScore` lazily loads and caches the model as a classmethod-level singleton (`cls.model`), driven by an injected `load_wrapper` (e.g. `joblib.load`) — this indirection is what lets the template stay ML-framework-agnostic.

### Key conventions to preserve when editing the template

- Imports inside `app/` are written relative to `app/` as a root (e.g. `from api.routes.api import router`, not `from app.api...`), because `make run` sets `PYTHONPATH=app/`. Tests, however, import as `from app.core.paginator import pagenation`, since pytest runs from the project root where `app/` is a real package. Keep this asymmetry in mind when adding new modules or tests.
- Deployment targets: Docker/`docker-compose.yml` (local) and GCP Cloud Run (`Dockerfile`) are actually wired up — see the generated `README.md` for the `gcloud` commands. AWS Lambda support is incomplete: `pyproject.toml` has an optional `mangum` dependency group and the README references a `main-aws-lambda.py` entry point and `sam build`/`sam deploy`, but that file and any SAM template are missing from the template, so Lambda deployment doesn't currently work out of the box.
- `cookiecutter.json`'s `_copy_without_render` list (`*ci.yaml`) exists so CI workflow files aren't mistakenly Jinja2-rendered; extend this list if new files contain literal `{{ }}`/`{% %}` that isn't a cookiecutter variable (e.g. GitHub Actions expression syntax).
