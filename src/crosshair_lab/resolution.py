"""Validated display resolutions and exact scale calculations."""

from dataclasses import dataclass
from decimal import Decimal
import re


_RESOLUTION_PATTERN = re.compile(r"(?P<width>[1-9]\d*)[xX](?P<height>[1-9]\d*)")


@dataclass(frozen=True, slots=True)
class Resolution:
    """A positive display width and height in pixels."""

    width: int
    height: int

    def __post_init__(self) -> None:
        if type(self.width) is not int or type(self.height) is not int:
            raise ValueError("resolution dimensions must be integers")
        if self.width <= 0 or self.height <= 0:
            raise ValueError("resolution dimensions must be positive")

    def horizontal_scale_to(self, other: "Resolution") -> Decimal:
        """Return the exact horizontal scale to another resolution."""
        return Decimal(other.width) / Decimal(self.width)

    def vertical_scale_to(self, other: "Resolution") -> Decimal:
        """Return the exact vertical scale to another resolution."""
        return Decimal(other.height) / Decimal(self.height)


def parse_resolution(text: str) -> Resolution:
    """Parse a resolution in ``WIDTHxHEIGHT`` form.

    Parameters
    ----------
    text : str
        Resolution text using a lower- or upper-case ``x`` separator.

    Returns
    -------
    Resolution
        Validated positive pixel dimensions.

    Raises
    ------
    ValueError
        If the text is not an exact positive resolution.
    """
    match = _RESOLUTION_PATTERN.fullmatch(text)
    if match is None:
        raise ValueError(f"invalid resolution {text!r}; expected WIDTHxHEIGHT")
    return Resolution(int(match.group("width")), int(match.group("height")))
