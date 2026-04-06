# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`bi-agent` is an early-stage Python project (v0.1.0) targeting Python 3.13+. The entry point is `main.py`.

## Package Management

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
uv sync          # Install dependencies
uv add <pkg>     # Add a dependency
uv run <cmd>     # Run a command within the venv
```

## Running the Project

```bash
uv run python main.py
```

## Linting

[Ruff](https://docs.astral.sh/ruff/) is used for linting and formatting.

```bash
uv run ruff check .        # Lint
uv run ruff check . --fix  # Auto-fix lint issues
uv run ruff format .       # Format code
```
