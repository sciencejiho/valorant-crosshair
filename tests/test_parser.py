"""Tests for valid and malformed crosshair parsing."""

import pytest

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


def test_parse_rejects_code_longer_than_input_limit() -> None:
    result = parse_crosshair("0;" + ("a" * 8192))

    assert result.code is None
    assert [item.code for item in result.errors] == ["code_too_long"]


def test_parse_rejects_more_than_512_delimited_atoms() -> None:
    result = parse_crosshair("0;" + ";".join(["x;1"] * 256))

    assert result.code is None
    assert [item.code for item in result.errors] == ["too_many_tokens"]
