"""Tests for the package-level foundation API."""

import crosshair_lab


def test_package_exports_foundation_api() -> None:
    expected = {
        "CrosshairCode",
        "CrosshairToken",
        "ConversionResult",
        "Diagnostic",
        "PARAMETERS",
        "ParameterChange",
        "ParameterSpec",
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
    }

    assert expected <= set(crosshair_lab.__all__)
