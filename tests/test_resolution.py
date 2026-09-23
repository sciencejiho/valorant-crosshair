"""Tests for display-resolution parsing and scale factors."""

import pytest

from crosshair_lab.resolution import Resolution, parse_resolution


def test_parse_resolution_accepts_lower_and_upper_x() -> None:
    assert parse_resolution("1920x1080") == Resolution(1920, 1080)
    assert parse_resolution("3840X2160") == Resolution(3840, 2160)


@pytest.mark.parametrize("text", ["", "1920", "0x1080", "-1x1080", "axb"])
def test_parse_resolution_rejects_invalid_values(text: str) -> None:
    with pytest.raises(ValueError):
        parse_resolution(text)


def test_resolution_exposes_exact_decimal_scale_factors() -> None:
    source = Resolution(2560, 1440)
    target = Resolution(3840, 2160)

    assert source.horizontal_scale_to(target).as_integer_ratio() == (3, 2)
    assert source.vertical_scale_to(target).as_integer_ratio() == (3, 2)
