"""Tests for the command-line conversion workflow."""

import json

from crosshair_lab.cli import main


CODE = "0;P;c;5;0t;1;0l;2;0v;2;0o;0"


def test_convert_command_prints_result_and_change_table(capsys) -> None:
    exit_code = main(
        ["convert", "--from", "1920x1080", "--to", "3840x2160", CODE]
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Scale factor: 2" in output
    assert "0l: 2 -> 4" in output
    assert "0;P;c;5;0t;2;0l;4;0v;4;0o;0" in output


def test_convert_json_is_machine_readable(capsys) -> None:
    exit_code = main(
        [
            "convert",
            "--json",
            "--from",
            "1920x1080",
            "--to",
            "3840x2160",
            CODE,
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["scale_factor"] == "2"
    assert payload["result_code"].endswith("0o;0")


def test_invalid_input_reports_stderr_and_nonzero(capsys) -> None:
    exit_code = main(
        ["convert", "--from", "1920x1080", "--to", "4kx2160", "0;s"]
    )
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "error:" in captured.err.lower()


def test_malformed_crosshair_reports_parser_diagnostic(capsys) -> None:
    exit_code = main(
        ["convert", "--from", "1920x1080", "--to", "3840x2160", "0;s"]
    )
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "no following value" in captured.err


def test_non_finite_custom_scale_reports_user_error(capsys) -> None:
    exit_code = main(
        [
            "convert",
            "--from",
            "1920x1080",
            "--to",
            "3840x2160",
            "--policy",
            "custom",
            "--scale",
            "NaN",
            CODE,
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "positive finite" in captured.err
