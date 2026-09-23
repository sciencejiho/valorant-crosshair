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
