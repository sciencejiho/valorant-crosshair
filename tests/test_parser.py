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
