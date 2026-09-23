# Repository Guidelines

## Project Structure & Module Organization

This repository is currently specification-first: `valorant_crosshair_lab_SPEC.md` defines the architecture and delivery milestones. Implement the Python package with a `src` layout under `src/crosshair_lab/`. Keep parsing, serialization, parameter metadata, conversion, and preview logic independent of interfaces. Place Textual code in `src/crosshair_lab/tui/`, PySide6 code in `src/crosshair_lab/gui/`, and CLI wiring in `src/crosshair_lab/cli.py`.

Mirror core modules in `tests/` (for example, `parser.py` with `tests/test_parser.py`). Store reusable crosshair fixtures in `examples/`, including the JUNiOR reference code from the specification.

## Build, Test, and Development Commands

The project skeleton and `pyproject.toml` have not been created yet. Once added, contributors should use a local virtual environment and expose standard commands:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
pytest
python -m crosshair_lab.cli --help
```

Use `pytest tests/test_parser.py -q` for a focused test run. Add formatter and linter commands to this section when those tools are configured in `pyproject.toml`.

## Coding Style & Naming Conventions

Target Python 3.12 or newer. Use four-space indentation, type annotations, and small modules with explicit responsibilities. Name modules, functions, and variables in `snake_case`; classes and dataclasses in `PascalCase`; constants in `UPPER_SNAKE_CASE`. Keep parameter meanings in one registry rather than scattering raw keys such as `0l` or `0t` throughout the code. UI layers must call shared core APIs instead of duplicating domain logic.

## Testing Guidelines

Use pytest and name files `test_*.py` and tests `test_<behavior>`. Cover valid and malformed parsing, lossless round trips, unknown-token preservation, explicit scaling and rounding policies, deterministic raster output, and stable candidate ordering. Treat the JUNiOR crosshair as a regression fixture. Every bug fix should include a failing test that demonstrates the defect.

## Commit & Pull Request Guidelines

No Git history is present, so no repository-specific convention can be inferred. Use concise, imperative commit subjects such as `Add lossless crosshair parser`, keeping each commit focused. Pull requests should identify the milestone addressed, summarize behavior changes, list verification commands, and link relevant issues. Include screenshots or recordings for TUI/GUI changes and call out assumptions about undocumented VALORANT behavior.

## Architecture & Safety

Preserve unknown parameters and token order during serialization. Keep geometric equivalence distinct from experimental raster similarity, and surface conversion policies and warnings to users. Do not add game-memory access, overlays, input automation, Riot API coupling, or automatic game-file modification; these are explicit non-goals.
