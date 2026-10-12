# SoL-Pi Visual (`solpi-visual`)

An isolated, opt-in example extracted from SIGIL's `qihang` branch. It adds
**Magnify** for inspecting existing image regions and **foreground render/build
waiting guidance** to avoid model turns spent only polling. The original profile's
local edit scope guidance is available as a separate switch.

[15-scene results and public preview](results/README.md#public-preview) provide
numeric charts and original source links without redistributing third-party media.
For authorized reviewers, the separate private archive contains 45 reference/baseline
videos and grading frames. Private archive metadata in
`results/media.json` and `results/hosting.json` is provided for authorized access
only; it contains no media or credentials. These are historical results, not new
measurements of this isolated example.

## What it does

| Setting | Behavior |
| --- | --- |
| `magnify` | Crops an existing image and interpolates its pixels. Returns PNG image blocks and a coordinate/hash receipt directly to Pi. An optional reference image uses its own independently selected box. |
| `awaitRender` | Adds guidance to await render/build results in the foreground when there is no independent work. It preserves normal asynchronous work when the host's timeout or recovery behavior requires it. |
| `localEditScope` | Guides each editing pass toward one supported discrepancy or coupled cause while preserving whole-scene requirements and final validation. |

All three settings default to `false`. The sample configuration enables the full
historical scene profile; disable `localEditScope` to use only Magnify and waiting
guidance. The waiting behavior is prompt guidance, not a shell override or a job
scheduler. Magnify does not render, generate detail, or make image-reading free.

## Isolation

- This directory is a separate Pi package with its own lockfile and checks. It
  does not import SoL-Pi core internals or copy the four original mechanisms.
  Its local Vitest configuration selects `*.check.ts` files so the parent's
  default test discovery does not pick up the example suite.
- The root package does not include or automatically load this example.
- Settings live only in the trusted project's
  `.pi/solpi-visual.json`. This example never reads or edits `sol-pi.json`
  and does not use user-wide example settings.
- Crops live under
  `<session-directory>/sol-pi-examples/solpi-visual/<session-id>/magnify/`.
  Ephemeral sessions use a private temporary directory. Artifacts remain after
  the session exits so receipts can be inspected; the caller owns cleanup.
- No videos, scene archives, trajectories, or credentials are bundled. Local
  preview media stays in ignored `output/`. Large demonstration assets live in
  [Belta/solpi-visual](https://huggingface.co/datasets/Belta/solpi-visual)
  on Hugging Face (private, authorized access only); `results/media.json` records their hashes
  and `results/hosting.json` pins the repository revision.

## Versions and source

[PROVENANCE.json](PROVENANCE.json) records the exact source paths and hashes.
SIGIL source links require access to the private repository; running this example
does not require cloning either private source repository.

- SIGIL scene implementation: `qihang` history at
  `4c227deb` (the initial scene-profile commit).
- SIGIL's frozen `agents/pi` gitlink:
  `0b4f4123ffe3e0f73b473c6d37e8e7009542875b`, reporting **Pi 0.81.1**.
- The initial SIGIL scene package was tested with **Pi 0.85.1**. The current
  `qihang` branch also contains later custom Pi/context changes; those are not
  copied into this example. Published upstream Pi 1.0.4 is used as the host.
- This example's development lock pins the published npm
  `@earendil-works/pi-coding-agent@1.0.4` after dependency security fixes. It does not vendor or patch Pi.
  The npm release and SIGIL's frozen Pi fork are distinct checkpoints. Tests of
  this example do not establish compatibility of the complete current SoL-Pi
  package with Pi 1.0.4 or reproduce the historical scene benchmark.

The crop implementation and three prompt policies come from the initial
scene-profile commit. The prompt policies are unchanged; the crop tool adds
bounded regular-file reads, PNG/JPEG format checks, encoded-output limits and
concurrent cache handling. The adapter uses separate example configuration
and storage, and retains that commit's five-argument Pi tool execution interface.
Later Pi hosts need their own compatibility validation.

## Install dependencies and check

Requirements: Node.js 22.19+, npm, Python 3.10+. Run from this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-magnify.txt
npm ci --ignore-scripts
npm run check
```

Python/Pillow are required for the Magnify tool and crop tests. Keep the virtual
environment active when running Pi: the tool invokes `python3` from PATH.
Dependencies remain local; these steps do not change a global Pi installation.

## Run in a scene project

Save this directory's absolute path, then move to the intended scene project:

```bash
export SOLPI_VISUAL_ROOT="$PWD"
cd /absolute/path/to/scene-project
mkdir -p .pi
cp "$SOLPI_VISUAL_ROOT/solpi-visual.example.json" .pi/solpi-visual.json
"$SOLPI_VISUAL_ROOT/node_modules/.bin/pi" \
  --extension "$SOLPI_VISUAL_ROOT/src/index.ts" --approve
```

If this example already has project settings, edit that file to preserve your
chosen switches. `--approve` trusts the selected project. Before trust approval,
project settings are ignored and the example stays disabled. Use `--approve`
only for projects you trust. Restart Pi after changing `.pi/solpi-visual.json`
or granting project trust. Configure the main
model and authentication through Pi's normal controls.

When using the example alongside an independently validated base SoL-Pi package,
keep base settings in `.pi/sol-pi.json` and these settings in
`.pi/solpi-visual.json`. Do not load SIGIL's full scene-profile package
at the same time: it already registers `magnify` and the same guidance.

## Magnify input

```json
{
  "image": "renders/front.png",
  "bbox": [120, 80, 260, 240],
  "reference": "reference/front.png",
  "referenceBbox": [100, 90, 250, 250],
  "scale": 2,
  "interpolation": "bicubic",
  "maxSide": 1024
}
```

Boxes use pixel edges in the EXIF-oriented displayed image, with a top-left
origin and exclusive right/bottom edges. Each box must be nonempty and entirely
inside its image. `reference` and `referenceBbox` must be supplied together.
Scale is 1–8; the default output-edge limit is 1024, with an explicit maximum of
4096 and an 8-million-pixel output limit. Inputs are single-frame RGB/RGBA/L/LA
PNG/JPEG images, at most 64 MiB and 32 million pixels. Each output PNG is
limited to 3,750,000 bytes before base64 encoding; reduce the box or scale when
this limit is reached. Provider-specific limits may be stricter. Sources are not overwritten.

Each receipt includes source/output hashes, original coordinates, interpolation
and coordinate mapping. Identical requests reuse verified crops; modified cache
artifacts cause an error rather than an overwrite.

The same crop tool can run directly:

```bash
python3 src/scene/magnify.py \
  --image /absolute/path/to/render.png --bbox 120 80 260 240 --scale 2 \
  --output-root ./output/magnify
```

## Validation and evidence

The example checks cover independent flags, rejected config values, project trust,
exact crop pixels, bounds, paired coordinates, source preservation, cache
integrity, and real Pi package loading. A deterministic faux provider verifies
that the next request receives the PNG and that a second user turn does not
duplicate the scene guidance. No paid model request is needed.

These checks establish integration behavior. They do not establish scene quality
or token savings. The historical SIGIL study combined local edit scope, optional
Magnify and waiting guidance; it reported lower known fees alongside lower mean
visual scores. It does not prove a stable individual Magnify benefit. See the
[historical evidence and limits](results/historical-evidence.md).

Local validation on 2026-10-12 used Node 26.0.0, npm 11.12.1, Python 3.14,
Pillow 11.3.0 and published Pi 1.0.4:

- Locked local dependency installation completed with install scripts disabled.
- TypeScript checks passed.
- Two Vitest files / eight tests passed, including real Pi loading and delivery
  of the crop to the next faux-provider request.
- Seven Python crop tests passed, including bounded inputs, encoded-output
  rejection, paired crop coordinates and concurrent cache reuse.
- Package inspection passed after excluding generated Python bytecode.

No scene benchmark or paid model evaluation was run. This is a locally validated
example, not a completed installation of the full SoL-Pi managed profile.

## Dependency audit status

The example now pins published Pi **1.0.4** and TypeBox **1.3.27**. Exact peer
versions intentionally limit installation to the validated host; validate a new
Pi version before widening them. Its source
is unmodified. A clean `npm ci --ignore-scripts` and `npm audit` on 2026-10-12
reported **zero vulnerabilities**, followed by the example's functional checks.
The earlier Pi 0.81.1 shrinkwrap retained vulnerable transitive dependencies;
that runtime is no longer the recommended installation. Historical checkpoint
and experiment data remain unchanged. This validates the standalone example,
not a complete current SoL-Pi base installation or a new scene benchmark.

## Public preview

Use the [public preview instructions](results/README.md#public-preview) to build
15-scene charts and original source links without redistributing third-party
videos, frames or crops. The full private/local video preview remains separate.
