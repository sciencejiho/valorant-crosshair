"""Tests for exact serialization and immutable editing."""

import pytest

from crosshair_lab.model import CrosshairCode, CrosshairToken, SectionMarker
from crosshair_lab.parser import parse_crosshair
from crosshair_lab.serializer import replace_parameter, serialize_crosshair


def _parsed(text: str) -> CrosshairCode:
    result = parse_crosshair(text)
    assert result.code is not None
    return result.code


def test_junior_code_round_trips_exactly(junior_code: str) -> None:
    assert serialize_crosshair(_parsed(junior_code)) == junior_code


def test_unknown_keys_duplicates_and_order_round_trip() -> None:
    text = "0;xyz;7;P;c;5;c;6;S;abc;-1.5"

    assert serialize_crosshair(_parsed(text)) == text


def test_trailing_separator_and_empty_sections_round_trip() -> None:
    text = "0;P;S;c;5;"

    assert serialize_crosshair(_parsed(text)) == text


def test_replace_parameter_changes_only_selected_occurrence() -> None:
    code = _parsed("0;P;c;5;c;7;S;c;9")

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
        replace_parameter(_parsed("0;P;c;5"), key="c", value=value, section="P")


def test_replace_parameter_rejects_negative_occurrence() -> None:
    with pytest.raises(ValueError):
        replace_parameter(
            _parsed("0;P;c;5"),
            key="c",
            value="7",
            section="P",
            occurrence=-1,
        )


def test_replace_parameter_reports_missing_match() -> None:
    with pytest.raises(KeyError):
        replace_parameter(_parsed("0;P;c;5"), key="0l", value="2", section="P")


def test_serialize_rejects_oversized_programmatic_model() -> None:
    code = CrosshairCode(
        prefix="0",
        elements=tuple(SectionMarker("P") for _ in range(512)),
        trailing_separator=False,
        source="",
    )

    with pytest.raises(ValueError, match="too many elements"):
        serialize_crosshair(code)
