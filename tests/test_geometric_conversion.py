"""Tests for deterministic geometric crosshair conversion."""

from decimal import Decimal

from crosshair_lab import CrosshairCode, parse_crosshair, serialize_crosshair
from crosshair_lab.conversion import convert_geometric
from crosshair_lab.policies import RoundingPolicy, ScalePolicy
from crosshair_lab.resolution import Resolution


def _parsed(text: str) -> CrosshairCode:
    result = parse_crosshair(text)
    assert result.code is not None
    return result.code


def test_1080p_to_4k_scales_present_dimensions_and_preserves_other_data() -> None:
    source = _parsed("0;P;c;5;0t;1;0l;2;0v;2;0o;0;xyz;7;S;c;5")

    result = convert_geometric(
        source,
        Resolution(1920, 1080),
        Resolution(3840, 2160),
    )

    assert result.scale_factor == Decimal("2")
    assert serialize_crosshair(result.converted) == (
        "0;P;c;5;0t;2;0l;4;0v;4;0o;0;xyz;7;S;c;5"
    )
    assert [(change.key, change.old_value, change.output_value) for change in result.changes] == [
        ("0t", Decimal("1"), Decimal("2")),
        ("0l", Decimal("2"), Decimal("4")),
        ("0v", Decimal("2"), Decimal("4")),
        ("0o", Decimal("0"), Decimal("0")),
    ]


def test_1440p_to_4k_uses_requested_rounding() -> None:
    result = convert_geometric(
        _parsed("0;P;0t;1;0l;2"),
        Resolution(2560, 1440),
        Resolution(3840, 2160),
        rounding_policy=RoundingPolicy.FLOOR,
    )

    assert serialize_crosshair(result.converted) == "0;P;0t;1;0l;3"


def test_invalid_scalable_value_is_preserved_with_warning() -> None:
    result = convert_geometric(
        _parsed("0;P;0t;thin;0l;-2"),
        Resolution(1920, 1080),
        Resolution(3840, 2160),
    )

    assert serialize_crosshair(result.converted) == "0;P;0t;thin;0l;-2"
    assert len(result.warnings) == 2


def test_mismatched_aspect_ratio_warns_and_duplicate_keys_both_convert() -> None:
    result = convert_geometric(
        _parsed("0;P;0l;1;0l;2"),
        Resolution(1920, 1080),
        Resolution(2560, 1080),
        scale_policy=ScalePolicy.VERTICAL,
    )

    assert serialize_crosshair(result.converted) == "0;P;0l;1;0l;2"
    assert len(result.changes) == 2
    assert any("aspect ratio" in warning for warning in result.warnings)
