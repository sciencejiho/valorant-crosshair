"""Explicit geometric scale and integer rounding policies."""

from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_UP
from enum import StrEnum

from crosshair_lab.resolution import Resolution


class ScalePolicy(StrEnum):
    """Axis policy used to derive a single geometric scale factor."""

    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    FIT = "fit"
    FILL = "fill"
    CUSTOM = "custom"


class RoundingPolicy(StrEnum):
    """Policy used to map an ideal dimension to an integer value."""

    NEAREST = "nearest"
    FLOOR = "floor"
    CEIL = "ceil"
    PRESERVE_ODD = "preserve_odd"
    PRESERVE_EVEN = "preserve_even"


def calculate_scale(
    source: Resolution,
    target: Resolution,
    policy: ScalePolicy,
    custom_scale: Decimal | None = None,
) -> Decimal:
    """Calculate one exact geometric scale factor.

    Parameters
    ----------
    source, target : Resolution
        Source and target display resolutions.
    policy : ScalePolicy
        Axis selection or fitting policy.
    custom_scale : Decimal or None, default None
        Positive factor required by the custom policy.

    Returns
    -------
    Decimal
        Positive scale factor.

    Raises
    ------
    ValueError
        If the custom policy lacks a positive finite factor.
    """
    horizontal = source.horizontal_scale_to(target)
    vertical = source.vertical_scale_to(target)
    if policy is ScalePolicy.VERTICAL:
        return vertical
    if policy is ScalePolicy.HORIZONTAL:
        return horizontal
    if policy is ScalePolicy.FIT:
        return min(horizontal, vertical)
    if policy is ScalePolicy.FILL:
        return max(horizontal, vertical)
    if (
        custom_scale is None
        or not custom_scale.is_finite()
        or custom_scale <= 0
    ):
        raise ValueError("custom scale must be a positive finite decimal")
    return custom_scale


def round_dimension(value: Decimal, policy: RoundingPolicy) -> Decimal:
    """Round a non-negative ideal dimension with an explicit policy.

    Parameters
    ----------
    value : Decimal
        Non-negative ideal dimension.
    policy : RoundingPolicy
        Integer rounding rule.

    Returns
    -------
    Decimal
        Integral Decimal result.

    Raises
    ------
    ValueError
        If the dimension is negative or non-finite.
    """
    if not value.is_finite() or value < 0:
        raise ValueError("dimension must be finite and non-negative")
    if policy is RoundingPolicy.NEAREST:
        return value.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    if policy is RoundingPolicy.FLOOR:
        return value.quantize(Decimal("1"), rounding=ROUND_FLOOR)
    if policy is RoundingPolicy.CEIL:
        return value.quantize(Decimal("1"), rounding=ROUND_CEILING)
    required_parity = 1 if policy is RoundingPolicy.PRESERVE_ODD else 0
    return _nearest_with_parity(value, required_parity)


def _nearest_with_parity(value: Decimal, parity: int) -> Decimal:
    floor_value = int(value.to_integral_value(rounding=ROUND_FLOOR))
    lower = floor_value if floor_value % 2 == parity else floor_value - 1
    upper = lower + 2
    if lower < 0:
        return Decimal(upper)
    lower_distance = value - Decimal(lower)
    upper_distance = Decimal(upper) - value
    return Decimal(lower if lower_distance <= upper_distance else upper)
