# AGENTS.md

## Project overview

Kepler is a Python experiment management tool for tracking, saving, and monitoring experiments. It uses Pydantic models, a Click CLI, a Textual TUI, and Pandas for data handling. Python 3.12+, managed with `uv`.

## Commands

### Install dependencies

```bash
uv sync
```

### Run tests

```bash
uv run pytest tests/
```

### Type checking

```bash
cd kepler && uv run mypy --python-version 3.12 --ignore-missing-imports .
```

### Run the TUI

```bash
uv run kepler tui
```

### Run CLI commands

```bash
uv run kepler list
uv run kepler info <experiment_id>
uv run kepler clean
```

## Project structure

```
kepler/
  api/          # Public API — experiment context manager, save helpers
  cli/          # Click CLI entry points (tui, list, info, clean)
  models/       # Pydantic models (Experiment, ExperimentList, ExperimentStatus), storage, logging
  tui/          # Textual terminal UI app
examples/       # Usage examples (scripts, notebook)
tests/          # Pytest tests (test_experiment.py)
pyproject.toml  # Project metadata, dependencies
mypy.ini        # Mypy configuration
uv.lock         # Locked dependencies
```

## Coding standards

- Use type hints on function signatures.
- Models use Pydantic `BaseModel`.
- CLI commands use Click.
- TUI uses Textual.
- `snake_case` for variables and functions, `PascalCase` for classes.
- Mypy config is lenient (`disallow_untyped_defs = False`, `ignore_missing_imports = True`) — do not tighten without discussion.

## Testing

- Tests live in `tests/`.
- Run the full suite: `uv run pytest tests/`
- Run a single test: `uv run pytest tests/test_experiment.py::TestExperiment::test_experiment_creation`
- Uses `pytest` with `tempfile` and `unittest.mock.patch` for isolation.
- No test database or external services required.

## Guardrails

- Do not push directly to `main`.
- Do not modify `uv.lock` by hand — use `uv add`/`uv remove` to change dependencies.
- Do not tighten mypy strictness settings without explicit approval.
