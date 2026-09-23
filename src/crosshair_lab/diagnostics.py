"""Structured diagnostics returned while parsing crosshair codes."""

from dataclasses import dataclass
from enum import StrEnum

from crosshair_lab.model import CrosshairCode


class Severity(StrEnum):
    """Diagnostic importance for user-supplied crosshair codes."""

    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class Diagnostic:
    """One stable parser diagnostic tied to a delimited token index."""

    severity: Severity
    code: str
    message: str
    token_index: int | None


@dataclass(frozen=True, slots=True)
class ParseResult:
    """A parsed code plus warnings or errors produced during parsing."""

    code: CrosshairCode | None
    diagnostics: tuple[Diagnostic, ...]

    @property
    def errors(self) -> tuple[Diagnostic, ...]:
        """Return all error diagnostics."""
        return tuple(
            item for item in self.diagnostics if item.severity is Severity.ERROR
        )

    @property
    def warnings(self) -> tuple[Diagnostic, ...]:
        """Return all warning diagnostics."""
        return tuple(
            item for item in self.diagnostics if item.severity is Severity.WARNING
        )

    @property
    def ok(self) -> bool:
        """Return whether parsing produced a code without errors."""
        return self.code is not None and not self.errors
