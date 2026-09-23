"""Command-line interface for crosshair inspection and conversion."""

import argparse
from collections.abc import Sequence
from decimal import Decimal, InvalidOperation
import json
import sys

from crosshair_lab.conversion import ConversionResult, convert_geometric
from crosshair_lab.parser import parse_crosshair
from crosshair_lab.policies import RoundingPolicy, ScalePolicy
from crosshair_lab.resolution import Resolution, parse_resolution
from crosshair_lab.serializer import serialize_crosshair


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line interface and return a process exit code.

    Parameters
    ----------
    argv : sequence of str or None, default None
        Arguments without the executable name. ``None`` reads ``sys.argv``.

    Returns
    -------
    int
        Zero on success and two for invalid user input.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "convert":
            return _run_convert(args)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    parser.print_help()
    return 2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="crosshair-lab")
    subparsers = parser.add_subparsers(dest="command")
    convert = subparsers.add_parser(
        "convert", help="convert dimensional parameters between resolutions"
    )
    convert.add_argument("code", help="VALORANT crosshair code")
    convert.add_argument("--from", dest="source", required=True, metavar="WIDTHxHEIGHT")
    convert.add_argument("--to", dest="target", required=True, metavar="WIDTHxHEIGHT")
    convert.add_argument(
        "--policy",
        choices=tuple(policy.value for policy in ScalePolicy),
        default=ScalePolicy.VERTICAL.value,
        help="scale policy (default: vertical)",
    )
    convert.add_argument(
        "--round",
        dest="rounding",
        choices=tuple(policy.value for policy in RoundingPolicy),
        default=RoundingPolicy.NEAREST.value,
        help="integer rounding policy (default: nearest)",
    )
    convert.add_argument("--scale", help="positive decimal for --policy custom")
    convert.add_argument("--json", action="store_true", help="emit JSON only")
    return parser


def _run_convert(args: argparse.Namespace) -> int:
    source = parse_resolution(args.source)
    target = parse_resolution(args.target)
    parsed = parse_crosshair(args.code)
    if parsed.code is None:
        messages = "; ".join(item.message for item in parsed.errors)
        raise ValueError(messages)

    scale_policy = ScalePolicy(args.policy)
    custom_scale = _custom_scale(args.scale, scale_policy)
    result = convert_geometric(
        parsed.code,
        source,
        target,
        scale_policy=scale_policy,
        rounding_policy=RoundingPolicy(args.rounding),
        custom_scale=custom_scale,
    )
    if args.json:
        print(json.dumps(_json_report(result), indent=2))
    else:
        print(_text_report(result))
    return 0


def _custom_scale(text: str | None, policy: ScalePolicy) -> Decimal | None:
    if text is None:
        return None
    if policy is not ScalePolicy.CUSTOM:
        raise ValueError("--scale requires --policy custom")
    try:
        return Decimal(text)
    except InvalidOperation as error:
        raise ValueError(f"invalid custom scale {text!r}") from error


def _json_report(result: ConversionResult) -> dict[str, object]:
    return {
        "source_resolution": _resolution_text(result.source_resolution),
        "target_resolution": _resolution_text(result.target_resolution),
        "scale_policy": result.scale_policy.value,
        "rounding_policy": result.rounding_policy.value,
        "scale_factor": format(result.scale_factor, "f"),
        "warnings": list(result.warnings),
        "changes": [
            {
                "section": change.section,
                "key": change.key,
                "old": format(change.old_value, "f"),
                "ideal": format(change.ideal_value, "f"),
                "output": format(change.output_value, "f"),
                "reason": change.reason,
            }
            for change in result.changes
        ],
        "result_code": serialize_crosshair(result.converted),
    }


def _text_report(result: ConversionResult) -> str:
    lines = [
        f"Source: {_resolution_text(result.source_resolution)}",
        f"Target: {_resolution_text(result.target_resolution)}",
        f"Scale policy: {result.scale_policy.value}",
        f"Rounding policy: {result.rounding_policy.value}",
        f"Scale factor: {result.scale_factor}",
    ]
    lines.extend(f"Warning: {warning}" for warning in result.warnings)
    lines.append("Changes:")
    lines.extend(
        f"  {change.key}: {change.old_value} -> {change.output_value} "
        f"(ideal {change.ideal_value})"
        for change in result.changes
    )
    lines.extend(("Result:", serialize_crosshair(result.converted)))
    return "\n".join(lines)


def _resolution_text(resolution: Resolution) -> str:
    return f"{resolution.width}x{resolution.height}"


if __name__ == "__main__":
    raise SystemExit(main())
