"""Lossless parser for semicolon-delimited VALORANT crosshair codes."""

from crosshair_lab.diagnostics import Diagnostic, ParseResult, Severity
from crosshair_lab.limits import MAX_ATOMS, MAX_CODE_LENGTH
from crosshair_lab.model import CrosshairCode, CrosshairElement, CrosshairToken
from crosshair_lab.model import SectionMarker


SECTION_MARKERS = frozenset({"P", "A", "S"})


def _diagnostic(
    severity: Severity,
    code: str,
    message: str,
    token_index: int | None,
) -> Diagnostic:
    return Diagnostic(severity, code, message, token_index)


def _split_atoms(text: str) -> tuple[list[str], bool, list[Diagnostic]]:
    atoms = text.split(";")
    trailing_separator = atoms[-1] == ""
    if trailing_separator:
        atoms.pop()

    diagnostics: list[Diagnostic] = []
    if atoms and atoms[-1] == "":
        diagnostics.append(
            _diagnostic(
                Severity.ERROR,
                "repeated_separator",
                "Only one trailing semicolon is permitted.",
                len(atoms),
            )
        )
    return atoms, trailing_separator, diagnostics


def _parse_elements(
    atoms: list[str],
    diagnostics: list[Diagnostic],
) -> list[CrosshairElement]:
    elements: list[CrosshairElement] = []
    seen: set[tuple[str | None, str]] = set()
    section: str | None = None
    index = 1

    for _ in range(MAX_ATOMS):
        if index >= len(atoms):
            return elements
        key = atoms[index]
        if key in SECTION_MARKERS:
            section = key
            elements.append(SectionMarker(key))
            index += 1
            continue
        if not key:
            diagnostics.append(
                _diagnostic(Severity.ERROR, "empty_key", "Parameter key is empty.", index)
            )
            index += 2
            continue
        if index + 1 >= len(atoms):
            diagnostics.append(
                _diagnostic(
                    Severity.ERROR,
                    "missing_value",
                    f"Parameter '{key}' has no following value.",
                    index,
                )
            )
            return elements
        if atoms[index + 1] in SECTION_MARKERS:
            diagnostics.append(
                _diagnostic(
                    Severity.ERROR,
                    "missing_value",
                    f"Parameter '{key}' has no value before a section marker.",
                    index,
                )
            )
            index += 1
            continue

        _append_parameter(
            elements,
            seen,
            diagnostics,
            CrosshairToken(key, atoms[index + 1], section),
            index,
        )
        index += 2
    raise RuntimeError("parser exhausted its bounded token budget")


def _append_parameter(
    elements: list[CrosshairElement],
    seen: set[tuple[str | None, str]],
    diagnostics: list[Diagnostic],
    token: CrosshairToken,
    index: int,
) -> None:
    if not token.value:
        diagnostics.append(
            _diagnostic(
                Severity.ERROR,
                "empty_value",
                f"Parameter '{token.key}' has an empty value.",
                index + 1,
            )
        )
    identity = (token.section, token.key)
    if identity in seen:
        diagnostics.append(
            _diagnostic(
                Severity.WARNING,
                "duplicate_parameter",
                f"Parameter '{token.key}' is duplicated in section {token.section!r}.",
                index,
            )
        )
    seen.add(identity)
    elements.append(token)


def parse_crosshair(text: str) -> ParseResult:
    """Parse a crosshair code without normalizing keys or values.

    Parameters
    ----------
    text : str
        Semicolon-delimited crosshair code.

    Returns
    -------
    ParseResult
        Parsed code and any diagnostics. Invalid input produces no code.
    """
    if len(text) > MAX_CODE_LENGTH:
        diagnostic = _diagnostic(
            Severity.ERROR,
            "code_too_long",
            f"Crosshair code exceeds {MAX_CODE_LENGTH} characters.",
            None,
        )
        return ParseResult(None, (diagnostic,))
    if not text.strip():
        diagnostic = _diagnostic(
            Severity.ERROR, "empty_code", "Crosshair code is empty.", None
        )
        return ParseResult(None, (diagnostic,))

    atoms, trailing_separator, diagnostics = _split_atoms(text)
    if len(atoms) > MAX_ATOMS:
        diagnostic = _diagnostic(
            Severity.ERROR,
            "too_many_tokens",
            f"Crosshair code exceeds {MAX_ATOMS} delimited atoms.",
            None,
        )
        return ParseResult(None, (diagnostic,))
    prefix = atoms[0]
    if not prefix:
        diagnostics.append(
            _diagnostic(
                Severity.ERROR,
                "empty_prefix",
                "Crosshair code prefix is empty.",
                0,
            )
        )
    elements = _parse_elements(atoms, diagnostics)

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
