"""Lossless parser for semicolon-delimited VALORANT crosshair codes."""

from crosshair_lab.diagnostics import Diagnostic, ParseResult, Severity
from crosshair_lab.model import CrosshairCode, CrosshairElement, CrosshairToken
from crosshair_lab.model import SectionMarker


SECTION_MARKERS = frozenset({"P", "A", "S"})


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
