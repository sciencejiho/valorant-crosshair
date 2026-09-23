# VALORANT Crosshair Lab
## Engineering Specification for a Python TUI + GUI Crosshair Analyzer and Converter

Status: Initial development specification  
Primary language: Python  
Primary target: Windows  
Primary use case: Analyze, edit, scale, compare, and experimentally reproduce VALORANT crosshairs across display resolutions, especially 1080p -> 4K.

---

# 1. Project Summary

VALORANT crosshair codes are compact serialized strings containing multiple groups of numeric parameters. They are convenient for importing/exporting configurations, but they are difficult to reason about manually.

The initial motivation for this project is a practical problem:

> A crosshair that looks and behaves correctly at 1920x1080 may not retain the same apparent size or rasterization behavior at 3840x2160.

A concrete example is the following JUNiOR crosshair:

```text
0;s;1;P;c;5;o;1;f;0;m;1;0l;2;0v;2;0g;1;0o;0;0a;1;0f;0;1b;0;S;c;5;s;0.7;o;1
```

A naive 2x conversion for a 1080p -> 2160p display would approximately transform dimensional parameters such as:

```text
t;1   -> t;2
0t;2  -> 0t;4
0l;2  -> 0l;4
0v;2  -> 0v;4
```

However, exact visual behavior may depend on integer pixel rasterization. A simple geometric scale can therefore preserve physical size while changing the apparent center or other pixel-grid artifacts.

The project should support both:

1. **Geometric conversion**
   - Preserve apparent crosshair size between resolutions.

2. **Raster-aware experimentation**
   - Search nearby integer parameter combinations for a visually similar crosshair whose apparent center, symmetry, and pixel coverage resemble the source.

The software should expose this functionality through:

- a Python library,
- a terminal user interface (TUI),
- and a desktop graphical user interface (GUI).

The underlying model and conversion engine must be shared across all interfaces.

---

# 2. Initial Project Goals

The first usable version should allow the user to:

1. Paste a VALORANT crosshair code.
2. Parse it into a structured representation.
3. Display known parameters with human-readable names.
4. Edit parameters individually.
5. Re-serialize the structure into a valid crosshair code.
6. Specify source and target resolutions.
7. Generate a geometric resolution conversion.
8. Preview source and converted crosshairs on a simulated pixel grid.
9. Compare multiple candidate conversions.
10. Export/copy any generated crosshair code.
11. Preserve unknown parameters rather than discarding them.
12. Use the same backend from both the TUI and GUI.

The first major target workflow is:

```text
Paste 1080p crosshair
    |
    v
Parse
    |
    v
Inspect dimensions
    |
    v
Set target: 3840x2160
    |
    +--> Exact geometric scaling
    |
    +--> Integer/raster-aware candidate search
    |
    v
Compare previews
    |
    v
Copy selected crosshair code
```

---

# 3. Non-Goals for the Initial Version

Do not make the initial version dependent on:

- VALORANT process memory.
- Game file modification.
- Riot APIs.
- Screen injection or overlays.
- Automated mouse or keyboard input.
- Anti-cheat interaction.
- Reading game memory.
- Automatically modifying VALORANT configuration files.
- Computer vision against a running VALORANT client.

The application should initially be a standalone offline crosshair code utility.

This keeps the project technically simple and avoids unnecessary coupling to the game client.

---

# 4. Design Principles

## 4.1 Separate Data Model from UI

The parser, serializer, converter, rasterizer, and candidate-search logic must not depend on TUI or GUI frameworks.

Preferred architecture:

```text
            +-------------------+
            | crosshair_core    |
            +-------------------+
              ^       ^       ^
              |       |       |
        +-----+       |       +------+
        |             |              |
     CLI/TUI        GUI          Unit tests
```

This allows future interfaces such as a web UI without rewriting the core logic.

## 4.2 Preserve Unknown Data

VALORANT crosshair codes may contain parameters that are not yet documented by this project.

Unknown key/value pairs must round-trip unchanged.

For example:

```text
input:
0;s;1;P;c;5;xyz;7;0l;2

parse -> edit 0l -> serialize

output:
0;s;1;P;c;5;xyz;7;0l;4
```

The application must not silently remove `xyz;7`.

## 4.3 Prefer Explicit Transformations

Do not implement a "magic convert" function whose behavior is opaque.

Every conversion should expose:

- source resolution,
- target resolution,
- scale factor,
- changed parameters,
- old values,
- new values,
- rounding method,
- warnings.

## 4.4 Treat Raster Behavior as Experimental

The geometric model and raster model are different concepts.

The program should clearly distinguish:

```text
Geometric equivalence
```

from:

```text
Raster-equivalent approximation
```

Do not imply that a mathematically scaled crosshair is guaranteed to behave identically in VALORANT.

---

# 5. Suggested Repository Layout

```text
valorant-crosshair-lab/
|
|-- README.md
|-- SPEC.md
|-- pyproject.toml
|-- LICENSE
|
|-- src/
|   `-- crosshair_lab/
|       |-- __init__.py
|       |
|       |-- model.py
|       |-- parser.py
|       |-- serializer.py
|       |-- parameters.py
|       |
|       |-- conversion/
|       |   |-- __init__.py
|       |   |-- geometric.py
|       |   |-- raster.py
|       |   `-- search.py
|       |
|       |-- preview/
|       |   |-- __init__.py
|       |   |-- rasterizer.py
|       |   `-- metrics.py
|       |
|       |-- tui/
|       |   |-- __init__.py
|       |   `-- app.py
|       |
|       |-- gui/
|       |   |-- __init__.py
|       |   `-- app.py
|       |
|       `-- cli.py
|
|-- tests/
|   |-- test_parser.py
|   |-- test_serializer.py
|   |-- test_roundtrip.py
|   |-- test_geometric_conversion.py
|   |-- test_rasterizer.py
|   `-- test_candidate_search.py
|
`-- examples/
    `-- crosshairs.json
```

---

# 6. Core Data Model

The parsed crosshair should not initially be represented as a loose dictionary only.

Use a model that can preserve:

- ordering,
- sections,
- duplicate keys if they occur,
- unknown parameters,
- source string.

Suggested conceptual structure:

```python
class CrosshairToken:
    key: str
    value: str
    section: str | None


class CrosshairCode:
    tokens: list[CrosshairToken]
```

A higher-level API may expose known properties:

```python
crosshair.inner_line_length_horizontal
crosshair.inner_line_length_vertical
crosshair.inner_line_thickness
crosshair.inner_line_offset
```

but serialization should still be based on the complete token list.

This prevents loss of information.

---

# 7. Parsing Strategy

A VALORANT crosshair string can initially be treated as a semicolon-delimited sequence.

Example:

```text
0;s;1;P;c;5;o;1;f;0;m;1;0l;2;0v;2;0g;1;0o;0;0a;1;0f;0;1b;0;S;c;5;s;0.7;o;1
```

Initial parser responsibilities:

1. Split on `;`.
2. Preserve original ordering.
3. Identify section markers where applicable.
4. Associate parameter keys with following values.
5. Recognize known parameters.
6. Preserve unknown ones.
7. Report malformed sequences rather than silently correcting them.

The parser should produce diagnostics such as:

```text
WARNING: unknown parameter 'xyz'
ERROR: parameter '0l' has no following value
WARNING: duplicate parameter '0o'
```

---

# 8. Parameter Registry

Create a central registry instead of scattering parameter meanings throughout the codebase.

Example:

```python
PARAMETERS = {
    "c": {
        "name": "color",
        "type": "int",
        "scalable": False,
    },
    "0t": {
        "name": "inner_line_thickness",
        "type": "float",
        "scalable": True,
    },
    "0l": {
        "name": "inner_line_length_horizontal",
        "type": "float",
        "scalable": True,
    },
    "0v": {
        "name": "inner_line_length_vertical",
        "type": "float",
        "scalable": True,
    },
    "0o": {
        "name": "inner_line_offset",
        "type": "float",
        "scalable": True,
    },
}
```

The registry should eventually include:

- canonical name,
- description,
- expected type,
- valid range if known,
- whether it is geometric,
- whether it is resolution-sensitive,
- section ownership,
- default value if known,
- whether omission is semantically meaningful.

Do not require the registry to be complete before the parser works.

---

# 9. Resolution Model

Create a simple immutable resolution type.

```python
@dataclass(frozen=True)
class Resolution:
    width: int
    height: int
```

Useful derived properties:

```python
aspect_ratio
vertical_scale_to(other)
horizontal_scale_to(other)
```

For 1920x1080 -> 3840x2160:

```text
horizontal scale = 2.0
vertical scale   = 2.0
```

For mismatched aspect ratios, geometric conversion should not silently choose one scale.

The user should be given explicit policies:

```text
Scale policy:
[ ] vertical
[ ] horizontal
[ ] uniform fit
[ ] uniform fill
[ ] custom
```

For VALORANT crosshairs, vertical scaling may be the most intuitive initial default because crosshair dimensions are ultimately perceived against screen height, but the implementation should make this policy explicit rather than hard-coded.

---

# 10. Geometric Conversion

The simplest converter should apply a numeric scale to parameters classified as geometric.

Example source:

```text
1920x1080
```

Target:

```text
3840x2160
```

Scale:

```text
2.0
```

Candidate transformation:

```text
0t: 2 -> 4
0l: 2 -> 4
0v: 2 -> 4
0o: 0 -> 0
```

The conversion result should be represented as an object:

```python
@dataclass
class ParameterChange:
    key: str
    old_value: float
    ideal_value: float
    output_value: float
    reason: str


@dataclass
class ConversionResult:
    source: CrosshairCode
    converted: CrosshairCode
    source_resolution: Resolution
    target_resolution: Resolution
    changes: list[ParameterChange]
    warnings: list[str]
```

---

# 11. Rounding Policies

Pixel-grid parameters may require integer values.

Support explicit rounding policies:

```text
nearest
floor
ceil
preserve_odd
preserve_even
```

Example:

```text
source = 1
scale = 1.5
ideal = 1.5
```

Candidates:

```text
floor   -> 1
nearest -> 2
ceil    -> 2
```

Parity-preserving modes may be useful because odd/even dimensions can change center alignment.

Example:

```text
preserve_odd(1.5) -> 1 or 3
preserve_even(1.5) -> 2
```

The exact choice should be exposed in diagnostics.

---

# 12. Raster-Aware Conversion

This is the feature that makes the project more interesting than a simple code editor.

A raster-aware conversion should search nearby integer combinations and rank them by how closely the target rendering resembles the source rendering.

Conceptually:

```text
Source crosshair
1920x1080
    |
    v
Render normalized preview
    |
    v
Target ideal scale
    |
    v
Generate nearby integer candidates
    |
    v
Render each target candidate
    |
    v
Compare metrics
    |
    v
Rank candidates
```

The search should initially vary only a small subset of parameters:

```text
0t
0l
0v
0o
```

Later versions may include:

```text
outline thickness
center dot size
outer lines
```

---

# 13. Candidate Generation

Given an ideal scaled value, search a small neighborhood.

Example:

```text
ideal 0t = 4.0
ideal 0l = 4.0
ideal 0v = 4.0
```

Candidate ranges:

```text
0t = 3..5
0l = 3..5
0v = 3..5
0o = 0..1
```

Cartesian search:

```text
3 * 3 * 3 * 2 = 54 candidates
```

This is trivial computationally.

Allow configurable search radius:

```text
radius = 1
radius = 2
```

Avoid an unnecessarily large combinatorial search in the initial implementation.

---

# 14. Preview Rasterizer

Implement an internal renderer that converts the structured crosshair into a small monochrome or RGBA bitmap.

The preview should be pixel-accurate according to the application's own model.

Important:

This is a **simulation**, not necessarily a perfect reimplementation of VALORANT's renderer.

The renderer should allow:

```text
zoom = 1x
zoom = 8x
zoom = 16x
zoom = 32x
```

At high zoom, each physical pixel should be clearly visible.

Example conceptual preview:

```text
.................
.................
.......##........
.......##........
....########.....
....########.....
.......##........
.......##........
.................
.................
```

For raster debugging, show the mathematical screen center separately:

```text
crosshair pixels
screen center
visual centroid
```

---

# 15. Raster Similarity Metrics

The search engine needs measurable comparison criteria.

Initial metrics:

## 15.1 Bounding Box

Compare:

```text
width
height
```

## 15.2 Pixel Area

Compare total number of rendered pixels.

## 15.3 Visual Centroid

For all rendered pixels:

```text
centroid_x = mean(x)
centroid_y = mean(y)
```

Compare the centroid relative to the mathematical aim point.

This is particularly important for crosshairs whose visual center is slightly displaced by rasterization.

## 15.4 Symmetry

Measure left/right and top/bottom symmetry.

## 15.5 Normalized Pixel Similarity

Scale both rendered images into a common normalized coordinate system and compare occupancy.

Possible metric:

```text
mean squared error
```

or:

```text
intersection over union
```

Do not over-engineer this initially.

A weighted score may be sufficient:

```text
score =
    0.35 * size_error
  + 0.35 * centroid_error
  + 0.20 * occupancy_error
  + 0.10 * symmetry_error
```

Weights should be configurable.

---

# 16. Important Experimental Concept: Visual Center vs Aim Center

The application should explicitly model two different centers:

```text
Aim center:
mathematical center of the screen.

Visual center:
centroid or perceived center of the rendered crosshair.
```

Define:

```text
visual_offset_x = visual_center_x - aim_center_x
visual_offset_y = visual_center_y - aim_center_y
```

Example:

```text
visual_offset_y = +0.5 px
```

would mean the visual center lies half a rendered pixel below the actual aim center.

The software should display this prominently because it is relevant to crosshairs intended to create a small visual aiming bias.

---

# 17. TUI Requirements

Recommended framework:

```text
Textual
```

Reason:

- mature Python TUI framework,
- interactive widgets,
- tables,
- text inputs,
- keyboard navigation,
- supports rich layouts,
- easier to maintain than building directly on curses.

Suggested TUI layout:

```text
+--------------------------------------------------------------+
| VALORANT Crosshair Lab                                      |
+--------------------------------------------------------------+
| Crosshair Code                                              |
| [..........................................................] |
+------------------------------+-------------------------------+
| Source                       | Target                        |
| 1920 x 1080                  | 3840 x 2160                  |
| Scale: 2.000                 | Mode: raster-aware           |
+------------------------------+-------------------------------+
| Parameter                    | Source | Ideal | Candidate     |
| Inner thickness (0t)         | 2      | 4.0   | 4             |
| Horizontal length (0l)       | 2      | 4.0   | 4             |
| Vertical length (0v)         | 2      | 4.0   | 3             |
| Offset (0o)                  | 0      | 0.0   | 0             |
+--------------------------------------------------------------+
| Preview                                                      |
|                                                              |
|              █████████                                       |
|                 ██                                           |
|                 ██     + aim center                           |
|                                                              |
+--------------------------------------------------------------+
| [G] Geometric  [R] Raster Search  [C] Copy  [Q] Quit         |
+--------------------------------------------------------------+
```

Required TUI operations:

```text
paste code
parse
edit parameter
select resolution
run geometric conversion
run raster search
select candidate
copy result
show diagnostics
```

---

# 18. GUI Requirements

Recommended initial framework:

```text
PySide6
```

Reasons:

- mature desktop toolkit,
- good Windows support,
- powerful custom drawing,
- appropriate for pixel-grid visualization,
- avoids browser/runtime dependency.

Suggested GUI layout:

```text
+------------------------------------------------------------------+
| Crosshair code                                                   |
| [______________________________________________________________] |
| [Parse] [Paste] [Copy Result]                                    |
+-----------------------+----------------------+-------------------+
| Parameters            | Source Preview       | Target Preview    |
|                       |                      |                   |
| 0t  2 -> 4            |      pixels          |      pixels       |
| 0l  2 -> 4            |                      |                   |
| 0v  2 -> 3            |                      |                   |
| 0o  0 -> 0            |                      |                   |
|                       |                      |                   |
+-----------------------+----------------------+-------------------+
| Source: 1920x1080     Target: 3840x2160     Scale: 2.000        |
| Mode: [Raster-aware v] Radius: [1]                               |
+------------------------------------------------------------------+
| Candidate ranking                                                |
| # | score | 0t | 0l | 0v | 0o | centroid Y | size error         |
| 1 | ...   | ...                                                |
+------------------------------------------------------------------+
```

Preview requirements:

- nearest-neighbor zoom,
- optional pixel grid,
- aim-center marker,
- visual-centroid marker,
- overlay source/target normalized views,
- zoom slider.

---

# 19. CLI

Even if TUI and GUI are the main user interfaces, a small CLI is useful for automation and tests.

Example:

```bash
crosshair-lab parse "0;s;1;P;c;5;..."
```

Example:

```bash
crosshair-lab convert \
  --from 1920x1080 \
  --to 3840x2160 \
  --mode geometric \
  "0;s;1;P;c;5;..."
```

Example:

```bash
crosshair-lab search \
  --from 1920x1080 \
  --to 3840x2160 \
  --radius 1 \
  "0;s;1;P;c;5;..."
```

---

# 20. JUNiOR Crosshair as Initial Regression Fixture

Add the following source crosshair as an initial test fixture:

```text
0;s;1;P;c;5;o;1;f;0;m;1;0l;2;0v;2;0g;1;0o;0;0a;1;0f;0;1b;0;S;c;5;s;0.7;o;1
```

Example file:

```json
{
  "name": "junior_reference",
  "source_resolution": [1920, 1080],
  "code": "0;s;1;P;c;5;o;1;f;0;m;1;0l;2;0v;2;0g;1;0o;0;0a;1;0f;0;1b;0;S;c;5;s;0.7;o;1"
}
```

The geometric 2x conversion should produce the expected dimensional changes according to the chosen parameter registry and default-value rules.

Important:

If a parameter is omitted because the game uses a default value, the converter needs a policy.

Two possible policies:

```text
minimal serialization
```

Preserve omitted defaults.

or:

```text
explicit serialization
```

Write the inferred value explicitly.

The application should eventually support both.

For development, prefer minimal serialization unless explicit output is required for reproducibility.

---

# 21. Round-Trip Requirements

The following should hold:

```python
serialize(parse(code)) == code
```

for valid unmodified codes whenever possible.

If formatting normalization is intentionally applied, then use semantic equality:

```python
parse(serialize(parse(code))) == parse(code)
```

Unknown parameters must survive.

---

# 22. Test Plan

## Parser

Test:

```text
normal code
unknown parameter
duplicate parameter
missing value
empty string
trailing semicolon
decimal value
negative value if encountered
```

## Serializer

Test:

```text
no changes
single change
multiple changes
unknown tokens preserved
order preserved
```

## Geometric Converter

Test:

```text
1080p -> 2160p = 2.0
1440p -> 2160p = 1.5
2160p -> 1080p = 0.5
same resolution = 1.0
non-matching aspect ratios
```

## Rasterizer

Test simple synthetic shapes whose pixel occupancy is known exactly.

## Candidate Search

Given a known source and target, verify:

- candidates are generated within bounds,
- scores are deterministic,
- the lowest score is returned first,
- tie-breaking is deterministic.

---

# 23. Suggested Dependency Set

Initial:

```text
Python >= 3.12
pydantic or dataclasses
rich
textual
PySide6
pytest
```

Optional later:

```text
numpy
Pillow
```

Avoid requiring NumPy until the raster metrics actually benefit from it.

A small grid can initially be represented using ordinary Python lists.

---

# 24. Packaging

Use `pyproject.toml`.

Suggested commands:

```text
crosshair-lab
crosshair-lab-tui
crosshair-lab-gui
```

Possible entry points:

```toml
[project.scripts]
crosshair-lab = "crosshair_lab.cli:main"
crosshair-lab-tui = "crosshair_lab.tui.app:main"
crosshair-lab-gui = "crosshair_lab.gui.app:main"
```

---

# 25. Development Milestones

## Milestone 1 — Parser and Serializer

Deliver:

- token model,
- parser,
- serializer,
- unknown-token preservation,
- round-trip tests.

Acceptance criterion:

```text
The JUNiOR reference code can be parsed, inspected, serialized, and reproduced without data loss.
```

## Milestone 2 — Parameter Registry

Deliver:

- known parameter metadata,
- human-readable names,
- editable typed values,
- inferred defaults where needed.

## Milestone 3 — Geometric Converter

Deliver:

- resolution model,
- scale calculation,
- scalable parameter classification,
- configurable rounding,
- conversion diagnostics.

Acceptance criterion:

```text
1920x1080 -> 3840x2160 produces a deterministic 2x dimensional conversion.
```

## Milestone 4 — Raster Preview

Deliver:

- simple renderer,
- zoomed pixel-grid display,
- aim-center marker,
- centroid calculation.

## Milestone 5 — Raster Candidate Search

Deliver:

- neighborhood candidate generation,
- similarity metrics,
- ranked results.

Acceptance criterion:

```text
For a target resolution, the program returns several nearby integer configurations ranked by similarity to the source.
```

## Milestone 6 — TUI

Deliver:

- paste/edit code,
- source/target resolutions,
- parameter table,
- conversion,
- candidate selection,
- copy result.

## Milestone 7 — GUI

Deliver:

- complete basic workflow,
- side-by-side preview,
- candidate table,
- interactive parameter controls.

---

# 26. Recommended Codex Task Order

Do not ask Codex to build the complete application in one pass.

Use small tasks.

## Task 1

```text
Create the Python project skeleton described in SPEC.md using a src layout and pytest.
Do not implement the GUI or TUI yet.
```

## Task 2

```text
Implement a lossless parser and serializer for semicolon-delimited VALORANT crosshair codes.
Unknown parameters and token ordering must be preserved.
Add unit tests using the JUNiOR reference code from SPEC.md.
```

## Task 3

```text
Implement the parameter registry and typed accessors for known crosshair parameters.
Do not remove unknown parameters.
```

## Task 4

```text
Implement Resolution, conversion result models, and geometric scaling.
Scaling policy and rounding policy must be explicit.
Add tests for 1080p -> 4K and 1440p -> 4K.
```

## Task 5

```text
Implement a simple deterministic rasterizer for the currently supported inner-line parameters.
The renderer must expose the mathematical aim center and visual pixel centroid.
Do not build a UI yet.
```

## Task 6

```text
Implement raster candidate generation and ranking.
Search only 0t, 0l, 0v, and 0o initially.
Keep the search radius configurable.
```

## Task 7

```text
Build a Textual TUI using the existing backend.
Do not duplicate parser or conversion logic inside the UI layer.
```

## Task 8

```text
Build a PySide6 GUI using the existing backend.
Provide side-by-side source and target previews with nearest-neighbor zoom.
```

---

# 27. First Useful MVP

The MVP does not need raster search.

A genuinely useful first release can consist of:

```text
Crosshair code
    ->
Parser
    ->
Human-readable parameter table
    ->
Source resolution
    ->
Target resolution
    ->
Scale dimensions
    ->
Output crosshair code
```

This is enough to validate:

- parser correctness,
- parameter understanding,
- serialization,
- UI architecture.

Raster-aware search should be the next feature after that foundation is stable.

---

# 28. Later Features

Possible later extensions:

## Presets

Save:

```text
Original
1080p
1440p
4K
custom
```

## Side-by-Side Diff

Show:

```text
0l: 2 -> 4
0v: 2 -> 3
0t: default(2) -> 4
```

## Crosshair Database

Local JSON/YAML collection of named crosshairs.

## Import From Clipboard

Detect a VALORANT crosshair code automatically.

## Shareable Conversion Report

Export:

```text
source code
source resolution
target resolution
conversion mode
result code
parameter diff
```

## Search Objective Profiles

Examples:

```text
Preserve apparent size
Preserve centroid
Preserve symmetry
Preserve thinness
Balanced
```

## Screenshot Calibration

Much later, allow the user to provide screenshots of the same crosshair at two resolutions and fit the simulator to observed rasterization.

This would be considerably more reliable than assuming that the internal preview exactly matches VALORANT's renderer.

---

# 29. Open Technical Questions

These should be investigated experimentally instead of assumed.

1. Which crosshair dimensions are expressed directly in framebuffer pixels?
2. Which values are scaled internally by VALORANT?
3. How does VALORANT round odd and even lengths around the screen center?
4. Does fullscreen resolution affect crosshair rasterization independently of desktop resolution?
5. Does UI scaling affect the renderer?
6. Are horizontal and vertical inner-line dimensions treated identically?
7. How are omitted default parameters serialized by the game?
8. Are decimal dimensional values accepted for every relevant parameter?
9. Does VALORANT quantize those decimals internally?
10. Is the crosshair rendered before or after any resolution scaling stage?

The project should keep empirical observations separate from assumptions.

---

# 30. Definition of Success

The project is successful when a user can paste a crosshair such as:

```text
0;s;1;P;c;5;o;1;f;0;m;1;0l;2;0v;2;0g;1;0o;0;0a;1;0f;0;1b;0;S;c;5;s;0.7;o;1
```

select:

```text
Source: 1920x1080
Target: 3840x2160
```

and receive:

1. a transparent explanation of every dimensional change,
2. a geometrically scaled candidate,
3. a pixel-grid preview,
4. several raster-aware alternative candidates,
5. measurements of visual-center displacement,
6. and a copyable VALORANT crosshair code.

The user should always be able to understand **why** a candidate differs from the source rather than receiving an unexplained transformed string.

---

# 31. Recommended Initial README Description

> VALORANT Crosshair Lab is a Python tool for parsing, inspecting, converting, and experimentally matching VALORANT crosshair codes across display resolutions. It provides a shared core library with terminal and desktop interfaces, including geometric resolution scaling, pixel-grid previews, and raster-aware candidate search.

---

# 32. Immediate Next Step

Start with the parser.

The first implementation target should be:

```text
input string
    ->
lossless tokenized representation
    ->
typed access to known parameters
    ->
edit one parameter
    ->
serialize
```

Do not begin with GUI rendering.

If the crosshair representation is designed correctly, the TUI, GUI, conversion engine, and later raster-search functionality can all be built cleanly on top of it.
