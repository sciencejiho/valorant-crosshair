# Parser and Serializer Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an installable Python package that losslessly parses, edits, and serializes VALORANT crosshair codes, with structured diagnostics and regression coverage for the JUNiOR reference code.

**Architecture:** Represent the input as an immutable ordered stream of section markers and key/value tokens so unknown keys, duplicates, section boundaries, and trailing delimiters survive round trips. Parsing returns a result object instead of raising for user input; editing and serialization operate only on successfully parsed models. The core remains independent of CLI, TUI, GUI, conversion, and raster dependencies.

**Tech Stack:** Python 3.12+, standard-library dataclasses and enums, setuptools via `pyproject.toml`, pytest 8, and uv for the local environment.

**Spec:** `valorant_crosshair_lab_SPEC.md` (Milestone 1; especially sections 4–8, 20–22, and 24–27)

## Global Constraints

- Target Python 3.12 or newer; Windows is the primary platform, but core modules must be platform-neutral.
- Preserve token order, duplicate keys, unknown key/value pairs, section markers, original source text, and one optional trailing semicolon.
- Treat `P`, `A`, and `S` as known standalone section markers; preserve them as stream elements.
- Keep parsing, editing, diagnostics, and serialization free of Textual, PySide6, NumPy, Pillow, game-process, Riot API, overlay, and input-automation dependencies.
- Do not infer parameter types or meanings in this slice; values remain strings until the parameter-registry plan.
- Do not initialize Git during execution without user authorization. If Git metadata exists by then, use the commit steps; otherwise skip only those commit commands.
- The current machine has uv 0.10.4 and uv-managed CPython 3.14.3, but no directly runnable `python`, `py`, or `pip`; use the explicit `.venv\Scripts\python.exe` path in every verification command.

## Review Focus

- Whitespace-only or empty input must return an `empty_code` error rather than raising (Task 3).
- Consecutive section markers must preserve empty section boundaries and remain serializable (Tasks 2 and 4).
- Duplicate keys in the same section must warn, while the same key in different sections must not warn (Task 3).
- An edited value containing `;` or an empty value must be rejected before serialization (Task 4).
- A single trailing semicolon must survive parse/serialize unchanged; repeated trailing delimiters must report malformed input (Tasks 2–4).

---

## Planned File Structure

- `pyproject.toml` — package metadata, Python floor, editable-install configuration, and pytest settings.
- `README.md` — current implemented scope, setup, and library example.
- `src/crosshair_lab/__init__.py` — small public API surface.
- `src/crosshair_lab/model.py` — immutable section, parameter, and crosshair stream models.
- `src/crosshair_lab/diagnostics.py` — diagnostic severity, diagnostic records, and parse result.
- `src/crosshair_lab/parser.py` — semicolon grammar, section tracking, malformed-input detection, and duplicate warnings.
- `src/crosshair_lab/serializer.py` — lossless stream serialization and immutable parameter replacement.
- `examples/crosshairs.json` — named JUNiOR regression fixture.
- `tests/conftest.py` — fixture loader.
- `tests/test_model.py` — model invariants.
- `tests/test_parser.py` — valid parsing and malformed-input behavior.
- `tests/test_serializer.py` — exact round trips and editing.
- `tests/test_public_api.py` — installed-package import contract.

## Explicit Follow-On Plans

This plan completes only the first independently testable subsystem. Create separate plans for the typed parameter registry; resolution and geometric conversion; rasterizer and similarity metrics; candidate search; CLI; Textual TUI; and PySide6 GUI. Those plans must build on the public interfaces established here without moving UI concerns into the core.

### Task 1: Package Skeleton and Immutable Model

**Files:**
- Create: `pyproject.toml`
- Create: `src/crosshair_lab/__init__.py`
- Create: `src/crosshair_lab/model.py`
- Create: `src/crosshair_lab/diagnostics.py`
- Create: `tests/test_model.py`

**Interfaces:**
- Consumes: No application code.
- Produces: `SectionMarker(name: str)`, `CrosshairToken(key: str, value: str, section: str | None)`, `CrosshairCode(prefix, elements, trailing_separator, source)`, `Severity`, `Diagnostic`, and `ParseResult`.

- [ ] **Step 1: Add package and test configuration**

Create `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=75"]
build-backend = "setuptools.build_meta"

[project]
name = "valorant-crosshair-lab"
version = "0.1.0"
description = "Parse, inspect, and convert VALORANT crosshair codes."
readme = "README.md"
requires-python = ">=3.12"
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=8.3,<9"]

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
addopts = "-ra"
testpaths = ["tests"]
```

Create a temporary minimal `README.md` containing the heading `# VALORANT Crosshair Lab` so editable installation can read the declared metadata. Task 5 replaces it with user-facing content.

Create `src/crosshair_lab/__init__.py` with:

```python
"""Core library for VALORANT Crosshair Lab."""
```

Bootstrap the environment using the already-installed interpreter:

```powershell
uv venv --python 3.14 .venv
uv pip install --python .venv\Scripts\python.exe -e ".[dev]"
```

Expected: uv creates `.venv` with CPython 3.14 and installs the editable package plus pytest.

- [ ] **Step 2: Write failing model tests**

Create `tests/test_model.py`:

```python
from crosshair_lab.diagnostics import Diagnostic, ParseResult, Severity
from crosshair_lab.model import CrosshairCode, CrosshairToken, SectionMarker


def test_crosshair_code_preserves_order_and_section_context() -> None:
    elements = (
        CrosshairToken("s", "1", None),
        SectionMarker("P"),
        CrosshairToken("c", "5", "P"),
        CrosshairToken("c", "7", "P"),
    )

    code = CrosshairCode(
        prefix="0",
        elements=elements,
        trailing_separator=False,
        source="0;s;1;P;c;5;c;7",
    )

    assert code.elements == elements
    assert code.parameters == (
        CrosshairToken("s", "1", None),
        CrosshairToken("c", "5", "P"),
        CrosshairToken("c", "7", "P"),
    )


def test_parse_result_reports_error_diagnostics() -> None:
    diagnostic = Diagnostic(
        severity=Severity.ERROR,
        code="empty_code",
        message="Crosshair code is empty.",
        token_index=None,
    )

    result = ParseResult(code=None, diagnostics=(diagnostic,))

    assert result.ok is False
    assert result.errors == (diagnostic,)
    assert result.warnings == ()
```

- [ ] **Step 3: Run the model tests and confirm the expected failure**

Run:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_model.py -v
```

Expected: collection fails because `crosshair_lab.diagnostics` and `crosshair_lab.model` do not exist.

- [ ] **Step 4: Implement the immutable model**

Create `src/crosshair_lab/model.py`:

```python
from dataclasses import dataclass
from typing import TypeAlias


@dataclass(frozen=True, slots=True)
class SectionMarker:
    """A standalone marker that changes the active crosshair section."""

    name: str


@dataclass(frozen=True, slots=True)
class CrosshairToken:
    """A lossless key/value token with its active section."""

    key: str
    value: str
    section: str | None


CrosshairElement: TypeAlias = SectionMarker | CrosshairToken


@dataclass(frozen=True, slots=True)
class CrosshairCode:
    """An immutable parsed crosshair stream."""

    prefix: str
    elements: tuple[CrosshairElement, ...]
    trailing_separator: bool
    source: str

    @property
    def parameters(self) -> tuple[CrosshairToken, ...]:
        return tuple(
            element
            for element in self.elements
            if isinstance(element, CrosshairToken)
        )
```

Create `src/crosshair_lab/diagnostics.py`:

```python
from dataclasses import dataclass
from enum import StrEnum

from crosshair_lab.model import CrosshairCode


class Severity(StrEnum):
    """Diagnostic importance for user-supplied crosshair codes."""

    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class Diagnostic:
    """One stable parser diagnostic tied to a delimited token index."""

    severity: Severity
    code: str
    message: str
    token_index: int | None


@dataclass(frozen=True, slots=True)
class ParseResult:
    """A parsed code plus warnings or errors produced during parsing."""

    code: CrosshairCode | None
    diagnostics: tuple[Diagnostic, ...]

    @property
    def errors(self) -> tuple[Diagnostic, ...]:
        return tuple(
            item for item in self.diagnostics if item.severity is Severity.ERROR
        )

    @property
    def warnings(self) -> tuple[Diagnostic, ...]:
        return tuple(
            item for item in self.diagnostics if item.severity is Severity.WARNING
        )

    @property
    def ok(self) -> bool:
        return self.code is not None and not self.errors
```

- [ ] **Step 5: Run the model tests**

Run:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_model.py -v
```

Expected: both tests pass through the uv-created virtual environment.

- [ ] **Step 6: Commit the model slice when Git is available**

```powershell
git add pyproject.toml README.md src/crosshair_lab tests/test_model.py
git commit -m "Add immutable crosshair token model"
```

Expected: one focused commit. If `git rev-parse --is-inside-work-tree` fails, do not run these commands.

### Task 2: Valid Lossless Parsing and Regression Fixture

**Files:**
- Create: `examples/crosshairs.json`
- Create: `tests/conftest.py`
- Create: `tests/test_parser.py`
- Create: `src/crosshair_lab/parser.py`

**Interfaces:**
- Consumes: Model and diagnostic types from Task 1.
- Produces: `parse_crosshair(text: str) -> ParseResult`; `SECTION_MARKERS: frozenset[str]`.

- [ ] **Step 1: Add the JUNiOR fixture**

Create `examples/crosshairs.json`:

```json
{
  "junior_reference": {
    "source_resolution": [1920, 1080],
    "code": "0;s;1;P;c;5;o;1;f;0;m;1;0l;2;0v;2;0g;1;0o;0;0a;1;0f;0;1b;0;S;c;5;s;0.7;o;1"
  }
}
```

Create `tests/conftest.py`:

```python
import json
from pathlib import Path

import pytest


@pytest.fixture
def junior_code() -> str:
    fixture_path = Path(__file__).parents[1] / "examples" / "crosshairs.json"
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    return str(payload["junior_reference"]["code"])
```

- [ ] **Step 2: Write failing valid-input parser tests**

Create `tests/test_parser.py`:

```python
from crosshair_lab.model import CrosshairToken, SectionMarker
from crosshair_lab.parser import parse_crosshair


def test_parse_junior_code_preserves_sections_and_values(junior_code: str) -> None:
    result = parse_crosshair(junior_code)

    assert result.ok
    assert result.code is not None
    assert result.code.prefix == "0"
    assert result.code.source == junior_code
    assert result.code.trailing_separator is False
    assert SectionMarker("P") in result.code.elements
    assert SectionMarker("S") in result.code.elements
    assert CrosshairToken("0l", "2", "P") in result.code.elements
    assert CrosshairToken("s", "0.7", "S") in result.code.elements


def test_parse_preserves_unknown_keys_and_raw_numeric_strings() -> None:
    result = parse_crosshair("0;xyz;-1.50;P;abc;007")

    assert result.ok
    assert result.code is not None
    assert result.code.parameters == (
        CrosshairToken("xyz", "-1.50", None),
        CrosshairToken("abc", "007", "P"),
    )


def test_parse_preserves_consecutive_sections() -> None:
    result = parse_crosshair("0;P;S;c;5")

    assert result.ok
    assert result.code is not None
    assert result.code.elements == (
        SectionMarker("P"),
        SectionMarker("S"),
        CrosshairToken("c", "5", "S"),
    )


def test_parse_records_one_trailing_separator() -> None:
    result = parse_crosshair("0;s;1;")

    assert result.ok
    assert result.code is not None
    assert result.code.trailing_separator is True
```

- [ ] **Step 3: Run the valid-input tests and confirm the expected failure**

Run:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_parser.py -v
```

Expected: collection fails because `crosshair_lab.parser` does not exist.

- [ ] **Step 4: Implement valid stream parsing**

Create `src/crosshair_lab/parser.py`:

```python
from crosshair_lab.diagnostics import Diagnostic, ParseResult, Severity
from crosshair_lab.model import CrosshairCode, CrosshairElement, CrosshairToken
from crosshair_lab.model import SectionMarker


SECTION_MARKERS = frozenset({"P", "A", "S"})


def parse_crosshair(text: str) -> ParseResult:
    """Parse a semicolon-delimited code without normalizing its values."""
    if not text.strip():
        diagnostic = Diagnostic(
            Severity.ERROR,
            "empty_code",
            "Crosshair code is empty.",
            None,
        )
        return ParseResult(None, (diagnostic,))

    atoms = text.split(";")
    trailing_separator = atoms[-1] == ""
    if trailing_separator:
        atoms.pop()

    prefix = atoms[0]
    elements: list[CrosshairElement] = []
    diagnostics: list[Diagnostic] = []
    section: str | None = None
    index = 1

    while index < len(atoms):
        key = atoms[index]
        if key in SECTION_MARKERS:
            section = key
            elements.append(SectionMarker(key))
            index += 1
            continue

        if index + 1 >= len(atoms):
            diagnostics.append(
                Diagnostic(
                    Severity.ERROR,
                    "missing_value",
                    f"Parameter '{key}' has no following value.",
                    index,
                )
            )
            break

        elements.append(CrosshairToken(key, atoms[index + 1], section))
        index += 2

    has_errors = any(
        item.severity is Severity.ERROR for item in diagnostics
    )
    code = None
    if not has_errors:
        code = CrosshairCode(
            prefix=prefix,
            elements=tuple(elements),
            trailing_separator=trailing_separator,
            source=text,
        )
    return ParseResult(code, tuple(diagnostics))
```

- [ ] **Step 5: Run the valid parser tests**

Run:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_parser.py -v
```

Expected: all four tests pass.

- [ ] **Step 6: Commit the valid parser slice when Git is available**

```powershell
git add examples/crosshairs.json tests/conftest.py tests/test_parser.py src/crosshair_lab/parser.py
git commit -m "Add lossless crosshair parser"
```

Expected: one focused commit. Skip these commands when no Git worktree exists.

### Task 3: Malformed-Input Diagnostics and Duplicate Detection

**Files:**
- Modify: `tests/test_parser.py`
- Modify: `src/crosshair_lab/parser.py`

**Interfaces:**
- Consumes: `parse_crosshair(text: str) -> ParseResult`.
- Produces: diagnostic codes `empty_code`, `empty_prefix`, `empty_key`, `empty_value`, `missing_value`, `repeated_separator`, and `duplicate_parameter`.

- [ ] **Step 1: Add failing malformed-input tests**

Append to `tests/test_parser.py`:

```python
import pytest


@pytest.mark.parametrize(
    ("text", "diagnostic_code"),
    [
        ("", "empty_code"),
        ("   ", "empty_code"),
        (";s;1", "empty_prefix"),
        ("0;;1", "empty_key"),
        ("0;s;", "missing_value"),
        ("0;s;;P;c;5", "empty_value"),
        ("0;s;P;c;5", "missing_value"),
        ("0;s", "missing_value"),
        ("0;s;1;;", "repeated_separator"),
    ],
)
def test_malformed_input_returns_an_error(
    text: str,
    diagnostic_code: str,
) -> None:
    result = parse_crosshair(text)

    assert result.ok is False
    assert result.code is None
    assert diagnostic_code in {item.code for item in result.errors}


def test_duplicate_parameter_in_one_section_warns_without_data_loss() -> None:
    result = parse_crosshair("0;P;c;5;c;7")

    assert result.ok
    assert result.code is not None
    assert [item.code for item in result.warnings] == ["duplicate_parameter"]
    assert result.code.parameters == (
        CrosshairToken("c", "5", "P"),
        CrosshairToken("c", "7", "P"),
    )


def test_same_key_in_different_sections_does_not_warn() -> None:
    result = parse_crosshair("0;P;c;5;S;c;5")

    assert result.ok
    assert result.warnings == ()
```

- [ ] **Step 2: Run the new diagnostics tests and confirm failures**

Run:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_parser.py -v
```

Expected: the valid parsing tests pass; malformed validation and duplicate-warning cases fail.

- [ ] **Step 3: Add explicit validation and duplicate tracking**

Update `parse_crosshair` in `src/crosshair_lab/parser.py` so the setup and loop include these checks:

```python
    atoms = text.split(";")
    trailing_separator = atoms[-1] == ""
    if trailing_separator:
        atoms.pop()

    diagnostics: list[Diagnostic] = []
    if atoms and atoms[-1] == "":
        diagnostics.append(
            Diagnostic(
                Severity.ERROR,
                "repeated_separator",
                "Only one trailing semicolon is permitted.",
                len(atoms),
            )
        )

    prefix = atoms[0]
    if not prefix:
        diagnostics.append(
            Diagnostic(
                Severity.ERROR,
                "empty_prefix",
                "Crosshair code prefix is empty.",
                0,
            )
        )

    elements: list[CrosshairElement] = []
    seen: set[tuple[str | None, str]] = set()
    section: str | None = None
    index = 1

    while index < len(atoms):
        key = atoms[index]
        if key in SECTION_MARKERS:
            section = key
            elements.append(SectionMarker(key))
            index += 1
            continue
        if not key:
            diagnostics.append(
                Diagnostic(
                    Severity.ERROR,
                    "empty_key",
                    "Parameter key is empty.",
                    index,
                )
            )
            index += 2
            continue
        if index + 1 >= len(atoms):
            diagnostics.append(
                Diagnostic(
                    Severity.ERROR,
                    "missing_value",
                    f"Parameter '{key}' has no following value.",
                    index,
                )
            )
            break

        if atoms[index + 1] in SECTION_MARKERS:
            diagnostics.append(
                Diagnostic(
                    Severity.ERROR,
                    "missing_value",
                    f"Parameter '{key}' has no value before a section marker.",
                    index,
                )
            )
            index += 1
            continue

        value = atoms[index + 1]
        if not value:
            diagnostics.append(
                Diagnostic(
                    Severity.ERROR,
                    "empty_value",
                    f"Parameter '{key}' has an empty value.",
                    index + 1,
                )
            )
        identity = (section, key)
        if identity in seen:
            diagnostics.append(
                Diagnostic(
                    Severity.WARNING,
                    "duplicate_parameter",
                    f"Parameter '{key}' is duplicated in section {section!r}.",
                    index,
                )
            )
        seen.add(identity)
        elements.append(CrosshairToken(key, value, section))
        index += 2
```

Keep the existing final `has_errors`, `CrosshairCode`, and `ParseResult` construction. This permits warnings alongside a valid code but returns `code=None` for any error.

- [ ] **Step 4: Run the complete parser tests**

Run:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_parser.py -v
```

Expected: all parser tests pass, including each parameterized malformed input.

- [ ] **Step 5: Commit diagnostics when Git is available**

```powershell
git add tests/test_parser.py src/crosshair_lab/parser.py
git commit -m "Report malformed and duplicate parameters"
```

Expected: one focused commit. Skip these commands when no Git worktree exists.

### Task 4: Lossless Serialization and Immutable Editing

**Files:**
- Create: `tests/test_serializer.py`
- Create: `src/crosshair_lab/serializer.py`

**Interfaces:**
- Consumes: a successful `CrosshairCode` and its ordered elements.
- Produces: `serialize_crosshair(code: CrosshairCode) -> str` and `replace_parameter(code, *, key, value, section=None, occurrence=0) -> CrosshairCode`.

- [ ] **Step 1: Write failing serializer and editor tests**

Create `tests/test_serializer.py`:

```python
import pytest

from crosshair_lab.model import CrosshairToken
from crosshair_lab.parser import parse_crosshair
from crosshair_lab.serializer import replace_parameter, serialize_crosshair


def parsed(text: str):
    result = parse_crosshair(text)
    assert result.code is not None
    return result.code


def test_junior_code_round_trips_exactly(junior_code: str) -> None:
    assert serialize_crosshair(parsed(junior_code)) == junior_code


def test_unknown_keys_duplicates_and_order_round_trip() -> None:
    text = "0;xyz;7;P;c;5;c;6;S;abc;-1.5"

    assert serialize_crosshair(parsed(text)) == text


def test_trailing_separator_and_empty_sections_round_trip() -> None:
    text = "0;P;S;c;5;"

    assert serialize_crosshair(parsed(text)) == text


def test_replace_parameter_changes_only_selected_occurrence() -> None:
    code = parsed("0;P;c;5;c;7;S;c;9")

    changed = replace_parameter(
        code,
        key="c",
        value="8",
        section="P",
        occurrence=1,
    )

    assert serialize_crosshair(changed) == "0;P;c;5;c;8;S;c;9"
    assert changed.source == code.source
    assert changed.parameters[0] == CrosshairToken("c", "5", "P")


@pytest.mark.parametrize("value", ["", "1;2"])
def test_replace_parameter_rejects_unserializable_value(value: str) -> None:
    with pytest.raises(ValueError):
        replace_parameter(parsed("0;P;c;5"), key="c", value=value, section="P")


def test_replace_parameter_rejects_negative_occurrence() -> None:
    with pytest.raises(ValueError):
        replace_parameter(
            parsed("0;P;c;5"),
            key="c",
            value="7",
            section="P",
            occurrence=-1,
        )


def test_replace_parameter_reports_missing_match() -> None:
    with pytest.raises(KeyError):
        replace_parameter(parsed("0;P;c;5"), key="0l", value="2", section="P")
```

- [ ] **Step 2: Run serializer tests and confirm the expected failure**

Run:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_serializer.py -v
```

Expected: collection fails because `crosshair_lab.serializer` does not exist.

- [ ] **Step 3: Implement serialization and replacement**

Create `src/crosshair_lab/serializer.py`:

```python
from dataclasses import replace

from crosshair_lab.model import CrosshairCode, CrosshairToken, SectionMarker


def serialize_crosshair(code: CrosshairCode) -> str:
    """Serialize the ordered stream without normalizing keys or values."""
    atoms = [code.prefix]
    for element in code.elements:
        if isinstance(element, SectionMarker):
            atoms.append(element.name)
        else:
            atoms.extend((element.key, element.value))
    serialized = ";".join(atoms)
    if code.trailing_separator:
        serialized += ";"
    return serialized


def replace_parameter(
    code: CrosshairCode,
    *,
    key: str,
    value: str,
    section: str | None = None,
    occurrence: int = 0,
) -> CrosshairCode:
    """Return a copy with one matching parameter value replaced."""
    if occurrence < 0:
        raise ValueError("occurrence must be non-negative")
    if not value or ";" in value:
        raise ValueError("value must be non-empty and cannot contain ';'")

    elements = list(code.elements)
    match_index = 0
    for index, element in enumerate(elements):
        if not isinstance(element, CrosshairToken):
            continue
        if element.key != key or element.section != section:
            continue
        if match_index == occurrence:
            elements[index] = replace(element, value=value)
            return replace(code, elements=tuple(elements))
        match_index += 1

    raise KeyError(
        f"No parameter {key!r} in section {section!r} "
        f"at occurrence {occurrence}."
    )
```

- [ ] **Step 4: Run serializer tests and the complete suite**

Run:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_serializer.py -v
.venv\Scripts\python.exe -m pytest -q
```

Expected: serializer tests pass and the complete suite has zero failures.

- [ ] **Step 5: Commit serialization when Git is available**

```powershell
git add tests/test_serializer.py src/crosshair_lab/serializer.py
git commit -m "Add lossless serialization and editing"
```

Expected: one focused commit. Skip these commands when no Git worktree exists.

### Task 5: Public API, Usage Documentation, and Release Verification

**Files:**
- Modify: `src/crosshair_lab/__init__.py`
- Create: `tests/test_public_api.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: parser, model, diagnostics, serializer, and editor interfaces from Tasks 1–4.
- Produces: stable package-level imports for `parse_crosshair`, `serialize_crosshair`, `replace_parameter`, model types, and diagnostic types.

- [ ] **Step 1: Write a failing public API test**

Create `tests/test_public_api.py`:

```python
import crosshair_lab


def test_package_exports_foundation_api() -> None:
    expected = {
        "CrosshairCode",
        "CrosshairToken",
        "Diagnostic",
        "ParseResult",
        "SectionMarker",
        "Severity",
        "parse_crosshair",
        "replace_parameter",
        "serialize_crosshair",
    }

    assert expected <= set(crosshair_lab.__all__)
```

- [ ] **Step 2: Run the public API test and confirm the expected failure**

Run:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_public_api.py -v
```

Expected: failure because `crosshair_lab.__all__` is not defined.

- [ ] **Step 3: Export the supported API**

Replace `src/crosshair_lab/__init__.py` with:

```python
"""Core library for VALORANT Crosshair Lab."""

from crosshair_lab.diagnostics import Diagnostic, ParseResult, Severity
from crosshair_lab.model import CrosshairCode, CrosshairToken, SectionMarker
from crosshair_lab.parser import parse_crosshair
from crosshair_lab.serializer import replace_parameter, serialize_crosshair

__all__ = [
    "CrosshairCode",
    "CrosshairToken",
    "Diagnostic",
    "ParseResult",
    "SectionMarker",
    "Severity",
    "parse_crosshair",
    "replace_parameter",
    "serialize_crosshair",
]
```

- [ ] **Step 4: Document the implemented slice**

Replace `README.md` with:

````markdown
# VALORANT Crosshair Lab

VALORANT Crosshair Lab is a Python 3.12+ project for parsing, inspecting,
converting, and experimentally matching VALORANT crosshair codes across
display resolutions.

The current foundation provides lossless parsing, structured diagnostics,
immutable parameter editing, and exact serialization. Conversion, previews,
and user interfaces remain outside this foundation slice.

## Development

```powershell
uv venv --python 3.14 .venv
uv pip install --python .venv\Scripts\python.exe -e ".[dev]"
.venv\Scripts\python.exe -m pytest
```

## Library Example

```python
from crosshair_lab import parse_crosshair, replace_parameter
from crosshair_lab import serialize_crosshair

result = parse_crosshair("0;P;c;5;0l;2")
if result.code is None:
    raise ValueError(result.errors)

edited = replace_parameter(
    result.code,
    key="0l",
    value="4",
    section="P",
)
print(serialize_crosshair(edited))
```

See `valorant_crosshair_lab_SPEC.md` for the architecture and roadmap.
````

- [ ] **Step 5: Run fresh installation and full verification**

Run in PowerShell:

```powershell
uv pip install --python .venv\Scripts\python.exe -e ".[dev]"
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe -c "from crosshair_lab import parse_crosshair, serialize_crosshair; s='0;P;c;5;0l;2;'; r=parse_crosshair(s); assert r.code is not None; assert serialize_crosshair(r.code) == s"
```

Expected: installation exits successfully, pytest reports zero failures, and the smoke command exits with no output.

- [ ] **Step 6: Inspect scope and repository state**

Run:

```powershell
rg -n "Textual|PySide6|numpy|Pillow" src tests
Get-ChildItem -Recurse src,tests,examples
```

Expected: the dependency search returns no matches in `src` or `tests`. The directory listing shows only the implementation and fixture files named in this plan.

- [ ] **Step 7: Commit the documented public API when Git is available**

```powershell
git add README.md src/crosshair_lab/__init__.py tests/test_public_api.py
git commit -m "Document parser foundation API"
```

Expected: one focused commit. Skip these commands when no Git worktree exists.

## Completion Criteria

- `uv pip install --python .venv\Scripts\python.exe -e ".[dev]"` succeeds on Python 3.12 or newer.
- `.venv\Scripts\python.exe -m pytest -q` reports zero failures.
- The JUNiOR fixture parses with `P` and `S` sections and round-trips byte-for-byte.
- Unknown key/value pairs, duplicate parameters, section boundaries, raw numeric text, ordering, and one trailing semicolon survive a successful round trip.
- Malformed input returns stable diagnostics without uncaught exceptions.
- Editing targets a specific key, section, and occurrence without mutating the original model.
- Core source imports no UI, raster, game-integration, or optional numeric libraries.
