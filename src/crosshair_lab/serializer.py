"""Lossless serialization and immutable editing for crosshair codes."""

from dataclasses import replace

from crosshair_lab.model import CrosshairCode, CrosshairToken, SectionMarker


def serialize_crosshair(code: CrosshairCode) -> str:
    """Serialize an ordered stream without normalizing its contents.

    Parameters
    ----------
    code : CrosshairCode
        Successfully parsed crosshair model.

    Returns
    -------
    str
        Semicolon-delimited code preserving the modeled stream.
    """
    atoms = [code.prefix]
    for element in code.elements:
        if isinstance(element, SectionMarker):
            atoms.append(element.name)
        else:
            atoms.extend((element.key, element.value))
    serialized = ";".join(atoms)
    if code.trailing_separator:
        serialized += ";"
    return serialized


def replace_parameter(
    code: CrosshairCode,
    *,
    key: str,
    value: str,
    section: str | None = None,
    occurrence: int = 0,
) -> CrosshairCode:
    """Return a copy with one matching parameter value replaced.

    Parameters
    ----------
    code : CrosshairCode
        Crosshair model to copy.
    key : str
        Exact parameter key to select.
    value : str
        Non-empty replacement value without semicolons.
    section : str or None, default None
        Section containing the parameter.
    occurrence : int, default 0
        Zero-based match to replace when a key is duplicated.

    Returns
    -------
    CrosshairCode
        New model with the selected token replaced.

    Raises
    ------
    ValueError
        If the occurrence or value cannot be serialized safely.
    KeyError
        If the requested parameter occurrence does not exist.
    """
    if occurrence < 0:
        raise ValueError("occurrence must be non-negative")
    if not value or ";" in value:
        raise ValueError("value must be non-empty and cannot contain ';'")

    elements = list(code.elements)
    match_index = 0
    for index, element in enumerate(elements):
        if not isinstance(element, CrosshairToken):
            continue
        if element.key != key or element.section != section:
            continue
        if match_index == occurrence:
            elements[index] = replace(element, value=value)
            return replace(code, elements=tuple(elements))
        match_index += 1

    raise KeyError(
        f"No parameter {key!r} in section {section!r} "
        f"at occurrence {occurrence}."
    )
