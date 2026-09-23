"""Core library for VALORANT Crosshair Lab."""

from crosshair_lab.conversion import (
    ConversionResult,
    ParameterChange,
    convert_geometric,
)
from crosshair_lab.diagnostics import Diagnostic, ParseResult, Severity
from crosshair_lab.model import CrosshairCode, CrosshairToken, SectionMarker
from crosshair_lab.parameters import PARAMETERS, ParameterSpec, scalable_parameter
from crosshair_lab.parser import parse_crosshair
from crosshair_lab.policies import RoundingPolicy, ScalePolicy
from crosshair_lab.resolution import Resolution, parse_resolution
from crosshair_lab.serializer import replace_parameter, serialize_crosshair

__all__ = (
    "CrosshairCode",
    "CrosshairToken",
    "ConversionResult",
    "Diagnostic",
    "PARAMETERS",
    "ParameterSpec",
    "ParameterChange",
    "ParseResult",
    "Resolution",
    "RoundingPolicy",
    "ScalePolicy",
    "SectionMarker",
    "Severity",
    "convert_geometric",
    "parse_crosshair",
    "parse_resolution",
    "replace_parameter",
    "scalable_parameter",
    "serialize_crosshair",
)
