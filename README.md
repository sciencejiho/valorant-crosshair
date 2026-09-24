<div align="center">

# VALORANT Crosshair Lab

**Losslessly inspect and convert VALORANT crosshair codes between display resolutions.**

[![CI](https://github.com/sciencejiho/valorant-crosshair/actions/workflows/ci.yml/badge.svg)](https://github.com/sciencejiho/valorant-crosshair/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub release](https://img.shields.io/github/v/release/sciencejiho/valorant-crosshair?display_name=tag&sort=semver)](https://github.com/sciencejiho/valorant-crosshair/releases)

```text
         │
      ───┼───       1920×1080  →  3840×2160
         │          0l: 2      →  4
```

[Quick start](#quick-start) · [How conversion works](#how-conversion-works) · [Roadmap](#roadmap) · [Contributing](CONTRIBUTING.md)

</div>

## Why Crosshair Lab?

A crosshair tuned at 1080p may feel different at 1440p or 4K. Crosshair Lab
parses VALORANT's compact code format, preserves every token, and scales only
known dimensional parameters. Each conversion reports the exact factor,
rounding policy, changed values, and warnings—no unexplained “magic” output.

## Features

- Lossless parse/edit/serialize round trips
- Unknown parameters, duplicates, ordering, sections, and trailing delimiters preserved
- Exact `Decimal`-based resolution scaling
- Vertical, horizontal, fit, fill, and custom scale policies
- Nearest, floor, ceil, odd, and even rounding policies
- Human-readable and machine-readable JSON reports
- Explicit aspect-ratio and malformed-value warnings
- Bounded input processing with no game-process or anti-cheat interaction

## Quick Start

Requires Python 3.12 or newer. Install directly from GitHub:

```powershell
python -m pip install "git+https://github.com/sciencejiho/valorant-crosshair.git"
```

Convert a crosshair from 1080p to 4K:

```powershell
crosshair-lab convert `
  --from 1920x1080 `
  --to 3840x2160 `
  "0;P;c;5;0t;1;0l;2;0v;2;0o;0"
```

Example result:

```text
Source: 1920x1080
Target: 3840x2160
Scale policy: vertical
Rounding policy: nearest
Scale factor: 2
Changes:
  0t: 1 -> 2 (ideal 2)
  0l: 2 -> 4 (ideal 4)
  0v: 2 -> 4 (ideal 4)
  0o: 0 -> 0 (ideal 0)
Result:
0;P;c;5;0t;2;0l;4;0v;4;0o;0
```

Add `--json` for automation:

```powershell
crosshair-lab convert --json --from 2560x1440 --to 3840x2160 "0;P;0l;2"
```

## How Conversion Works

The default scale uses screen height:

```text
scale = target height / source height
```

For 1920×1080 → 3840×2160, the factor is exactly `2`. Only dimensional
parameters already present in the code are transformed; omitted defaults are
not invented.

| Option | Values | Default |
|---|---|---|
| `--policy` | `vertical`, `horizontal`, `fit`, `fill`, `custom` | `vertical` |
| `--round` | `nearest`, `floor`, `ceil`, `preserve_odd`, `preserve_even` | `nearest` |
| `--scale` | Positive finite decimal used with `--policy custom` | — |
| `--json` | Emit a structured JSON report | off |

Currently scalable keys:

| Key | Meaning |
|---|---|
| `t` | Outline thickness |
| `z` | Center-dot size |
| `0t`, `1t` | Inner/outer line thickness |
| `0l`, `1l` | Inner/outer horizontal length |
| `0v`, `1v` | Inner/outer vertical length |
| `0o`, `1o` | Inner/outer line offset |

## Python API

```python
from crosshair_lab import Resolution, convert_geometric, parse_crosshair
from crosshair_lab import serialize_crosshair

parsed = parse_crosshair("0;P;0t;1;0l;2")
if parsed.code is None:
    raise ValueError(parsed.errors)

result = convert_geometric(
    parsed.code,
    Resolution(1920, 1080),
    Resolution(3840, 2160),
)
print(serialize_crosshair(result.converted))
```

## Development

```powershell
git clone https://github.com/sciencejiho/valorant-crosshair.git
cd valorant-crosshair
uv venv --python 3.14 .venv
uv pip install --python .venv\Scripts\python.exe -e ".[dev]"
.venv\Scripts\python.exe -m pytest
uv build
```

The suite covers parser losslessness, malformed inputs, resource limits,
scaling, rounding, conversion reports, and CLI behavior.

## Roadmap

- Pixel-grid crosshair preview
- Raster-aware candidate search and similarity ranking
- Desktop GUI with side-by-side source/target visualization
- Interactive terminal UI
- Saved presets and shareable conversion reports

See [the engineering specification](valorant_crosshair_lab_SPEC.md) for the
long-term architecture.

## Safety and Accuracy

Crosshair Lab is an offline code utility. It does not read game memory, modify
VALORANT files, inject overlays, automate input, or interact with anti-cheat.
Geometric equivalence does not guarantee identical in-game rasterization;
raster-aware matching remains experimental future work.

## License and Disclaimer

Released under the [MIT License](LICENSE). VALORANT is a trademark of Riot
Games, Inc. This project is community-made and is not affiliated with or
endorsed by Riot Games.
