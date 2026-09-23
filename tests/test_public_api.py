import crosshair_lab


def test_package_exports_foundation_api() -> None:
    expected = {
        "CrosshairCode",
        "CrosshairToken",
        "Diagnostic",
        "ParseResult",
        "SectionMarker",
        "Severity",
        "parse_crosshair",
        "replace_parameter",
        "serialize_crosshair",
    }

    assert expected <= set(crosshair_lab.__all__)
