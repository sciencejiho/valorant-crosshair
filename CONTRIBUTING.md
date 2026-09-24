# Contributing

Thanks for helping improve VALORANT Crosshair Lab.

## Set Up the Project

```powershell
git clone https://github.com/sciencejiho/valorant-crosshair.git
cd valorant-crosshair
uv venv --python 3.14 .venv
uv pip install --python .venv\Scripts\python.exe -e ".[dev]"
.venv\Scripts\python.exe -m pytest
```

Python 3.12 and newer are supported. Keep parser, conversion, and preview logic
inside the shared core; interfaces must not duplicate domain behavior.

## Make a Change

1. Create a focused branch from `main`.
2. Add a failing pytest that describes the behavior being changed.
3. Implement the smallest complete change.
4. Run `.venv\Scripts\python.exe -m pytest -q` and `uv build`.
5. Update user documentation when commands or output change.

Use four-space indentation, type annotations, `snake_case` functions and
modules, `PascalCase` classes, and concise imperative commits such as
`Add raster preview metrics`.

## Pull Requests

Explain the problem and solution, link relevant issues, and list verification
commands. Include screenshots or recordings for future GUI/TUI changes. Call
out assumptions about undocumented VALORANT behavior and keep empirical
observations separate from simulator behavior.
