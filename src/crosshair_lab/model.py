"""Immutable domain objects for parsed VALORANT crosshair codes."""

from dataclasses import dataclass
from typing import TypeAlias


@dataclass(frozen=True, slots=True)
class SectionMarker:
    """A standalone marker that changes the active crosshair section."""

    name: str


@dataclass(frozen=True, slots=True)
class CrosshairToken:
    """A lossless key/value token with its active section."""

    key: str
    value: str
    section: str | None


CrosshairElement: TypeAlias = SectionMarker | CrosshairToken


@dataclass(frozen=True, slots=True)
class CrosshairCode:
    """An immutable parsed crosshair stream."""

    prefix: str
    elements: tuple[CrosshairElement, ...]
    trailing_separator: bool
    source: str

    @property
    def parameters(self) -> tuple[CrosshairToken, ...]:
        """Return parameter tokens in their original order."""
        return tuple(
            element
            for element in self.elements
            if isinstance(element, CrosshairToken)
        )
