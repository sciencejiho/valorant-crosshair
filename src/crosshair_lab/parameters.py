"""Central metadata registry for known crosshair parameters."""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True, slots=True)
class ParameterSpec:
    """Metadata describing one known crosshair parameter."""

    key: str
    name: str
    scalable: bool


_SPECS = (
    ParameterSpec("t", "outline_thickness", True),
    ParameterSpec("z", "center_dot_size", True),
    ParameterSpec("0t", "inner_line_thickness", True),
    ParameterSpec("0l", "inner_line_length_horizontal", True),
    ParameterSpec("0v", "inner_line_length_vertical", True),
    ParameterSpec("0o", "inner_line_offset", True),
    ParameterSpec("1t", "outer_line_thickness", True),
    ParameterSpec("1l", "outer_line_length_horizontal", True),
    ParameterSpec("1v", "outer_line_length_vertical", True),
    ParameterSpec("1o", "outer_line_offset", True),
)

PARAMETERS: Mapping[str, ParameterSpec] = MappingProxyType(
    {spec.key: spec for spec in _SPECS}
)


def scalable_parameter(key: str) -> ParameterSpec | None:
    """Return scalable metadata for a key, if supported."""
    spec = PARAMETERS.get(key)
    if spec is None or not spec.scalable:
        return None
    return spec
