"""Tests for geometric scale and rounding policies."""

from decimal import Decimal

import pytest

from crosshair_lab.policies import (
    RoundingPolicy,
    ScalePolicy,
    calculate_scale,
    round_dimension,
)
from crosshair_lab.resolution import Resolution


SOURCE = Resolution(1920, 1080)
TARGET = Resolution(2560, 1440)


def test_scale_policies_are_explicit() -> None:
    four_thirds = Decimal("1.333333333333333333333333333")

    assert calculate_scale(SOURCE, TARGET, ScalePolicy.VERTICAL) == four_thirds
    assert calculate_scale(SOURCE, TARGET, ScalePolicy.HORIZONTAL) == four_thirds
    assert calculate_scale(
        SOURCE, Resolution(2560, 1080), ScalePolicy.FIT
    ) == Decimal("1")
    assert calculate_scale(
        SOURCE, Resolution(2560, 1080), ScalePolicy.FILL
    ) == four_thirds


def test_custom_scale_requires_positive_value() -> None:
    assert calculate_scale(
        SOURCE, TARGET, ScalePolicy.CUSTOM, Decimal("1.25")
    ) == Decimal("1.25")
    with pytest.raises(ValueError):
        calculate_scale(SOURCE, TARGET, ScalePolicy.CUSTOM)
    with pytest.raises(ValueError):
        calculate_scale(SOURCE, TARGET, ScalePolicy.CUSTOM, Decimal("0"))


@pytest.mark.parametrize(
    ("policy", "expected"),
    [
        (RoundingPolicy.NEAREST, Decimal("2")),
        (RoundingPolicy.FLOOR, Decimal("1")),
        (RoundingPolicy.CEIL, Decimal("2")),
        (RoundingPolicy.PRESERVE_ODD, Decimal("1")),
        (RoundingPolicy.PRESERVE_EVEN, Decimal("2")),
    ],
)
def test_rounding_policies_handle_half_deterministically(
    policy: RoundingPolicy,
    expected: Decimal,
) -> None:
    assert round_dimension(Decimal("1.5"), policy) == expected


def test_nearest_rounds_half_up_instead_of_to_even() -> None:
    assert round_dimension(Decimal("2.5"), RoundingPolicy.NEAREST) == Decimal("3")


def test_rounding_rejects_negative_dimensions() -> None:
    with pytest.raises(ValueError):
        round_dimension(Decimal("-0.1"), RoundingPolicy.NEAREST)
