"""Tests for the centralized crosshair parameter registry."""

from crosshair_lab.parameters import scalable_parameter


def test_registry_marks_supported_dimensions_as_scalable() -> None:
    keys = ("t", "z", "0t", "0l", "0v", "0o", "1t", "1l", "1v", "1o")

    for key in keys:
        spec = scalable_parameter(key)
        assert spec is not None
        assert spec.scalable


def test_registry_does_not_scale_opacity_or_unknown_keys() -> None:
    assert scalable_parameter("0a") is None
    assert scalable_parameter("xyz") is None
