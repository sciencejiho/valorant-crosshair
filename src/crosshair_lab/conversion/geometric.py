"""Deterministic geometric crosshair conversion between resolutions."""

from dataclasses import dataclass, replace
from decimal import Decimal, InvalidOperation

from crosshair_lab.limits import MAX_ELEMENTS
from crosshair_lab.model import CrosshairCode, CrosshairToken
from crosshair_lab.parameters import scalable_parameter
from crosshair_lab.policies import (
    RoundingPolicy,
    ScalePolicy,
    calculate_scale,
    round_dimension,
)
from crosshair_lab.resolution import Resolution


@dataclass(frozen=True, slots=True)
class ParameterChange:
    """One dimensional parameter transformation."""

    section: str | None
    key: str
    old_value: Decimal
    ideal_value: Decimal
    output_value: Decimal
    reason: str


@dataclass(frozen=True, slots=True)
class ConversionResult:
    """Complete geometric conversion result and diagnostics."""

    source: CrosshairCode
    converted: CrosshairCode
    source_resolution: Resolution
    target_resolution: Resolution
    scale_policy: ScalePolicy
    rounding_policy: RoundingPolicy
    scale_factor: Decimal
    changes: tuple[ParameterChange, ...]
    warnings: tuple[str, ...]


def convert_geometric(
    code: CrosshairCode,
    source_resolution: Resolution,
    target_resolution: Resolution,
    *,
    scale_policy: ScalePolicy = ScalePolicy.VERTICAL,
    rounding_policy: RoundingPolicy = RoundingPolicy.NEAREST,
    custom_scale: Decimal | None = None,
) -> ConversionResult:
    """Scale present dimensional parameters between two resolutions.

    Parameters
    ----------
    code : CrosshairCode
        Successfully parsed source code.
    source_resolution, target_resolution : Resolution
        Displays used to derive the geometric factor.
    scale_policy : ScalePolicy, default ScalePolicy.VERTICAL
        Axis or fitting rule used for the factor.
    rounding_policy : RoundingPolicy, default RoundingPolicy.NEAREST
        Integer mapping applied to every ideal dimension.
    custom_scale : Decimal or None, default None
        Positive factor for the custom scale policy.

    Returns
    -------
    ConversionResult
        Converted model, per-parameter changes, and warnings.
    """
    if len(code.elements) > MAX_ELEMENTS:
        raise ValueError(f"crosshair has too many elements; maximum is {MAX_ELEMENTS}")
    factor = calculate_scale(
        source_resolution, target_resolution, scale_policy, custom_scale
    )
    elements = list(code.elements)
    changes: list[ParameterChange] = []
    warnings = _resolution_warnings(source_resolution, target_resolution)

    for index in range(MAX_ELEMENTS):
        if index >= len(elements):
            break
        element = elements[index]
        if not isinstance(element, CrosshairToken):
            continue
        converted, change, warning = _convert_token(element, factor, rounding_policy)
        elements[index] = converted
        if change is not None:
            changes.append(change)
        if warning is not None:
            warnings.append(warning)

    return ConversionResult(
        source=code,
        converted=replace(code, elements=tuple(elements)),
        source_resolution=source_resolution,
        target_resolution=target_resolution,
        scale_policy=scale_policy,
        rounding_policy=rounding_policy,
        scale_factor=factor,
        changes=tuple(changes),
        warnings=tuple(warnings),
    )


def _resolution_warnings(source: Resolution, target: Resolution) -> list[str]:
    horizontal = source.horizontal_scale_to(target)
    vertical = source.vertical_scale_to(target)
    if horizontal == vertical:
        return []
    return [
        "Source and target aspect ratios differ: "
        f"horizontal scale={horizontal}, vertical scale={vertical}."
    ]


def _convert_token(
    token: CrosshairToken,
    factor: Decimal,
    rounding_policy: RoundingPolicy,
) -> tuple[CrosshairToken, ParameterChange | None, str | None]:
    if scalable_parameter(token.key) is None:
        return token, None, None
    try:
        old_value = Decimal(token.value)
    except InvalidOperation:
        return token, None, f"Parameter {token.key!r} is not numeric; preserved."
    if not old_value.is_finite() or old_value < 0:
        return token, None, f"Parameter {token.key!r} is not non-negative; preserved."

    ideal_value = old_value * factor
    output_value = round_dimension(ideal_value, rounding_policy)
    converted = replace(token, value=format(output_value, "f"))
    change = ParameterChange(
        section=token.section,
        key=token.key,
        old_value=old_value,
        ideal_value=ideal_value,
        output_value=output_value,
        reason=f"{rounding_policy.value} rounding after {factor}x scale",
    )
    return converted, change, None
