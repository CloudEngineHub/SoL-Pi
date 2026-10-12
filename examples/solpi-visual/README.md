# SoL-Pi Visual

A visual scene reconstruction example for SoL-Pi. It adds image-region inspection,
focused edits and guidance to wait for renders when there is no other work to do.

## Usage

Requirements: the parent repository's Node.js dependencies, Python 3.10+,
and Blender for scene reconstruction.

From the SoL-Pi repository root:

```bash
npm ci --ignore-scripts
export SOLPI_ROOT="$PWD"
python3 -m venv "$SOLPI_ROOT/.pi/visual-venv"
source "$SOLPI_ROOT/.pi/visual-venv/bin/activate"
python -m pip install Pillow==11.3.0
```

In your scene project, create `.pi/solpi-visual.json` with the following settings.
If the file already exists, update its switches instead of replacing it.

```json
{
  "version": 1,
  "localEditScope": true,
  "magnify": true,
  "awaitRender": true
}
```

Start Pi from that project, keeping the Python environment active:

```bash
cd /path/to/scene-project
"$SOLPI_ROOT/node_modules/.bin/pi" --approve \
  --extension "$SOLPI_ROOT/src/sol-pi/index.ts" \
  --extension "$SOLPI_ROOT/examples/solpi-visual/src/index.ts"
```

`--approve` trusts the project; use it only for projects you trust. Configure the
base SoL-Pi features using the [root README](../../README.md), and select your model
and authentication through Pi. This example uses the parent's installed Pi
(currently tested with 0.85.1) and does not install another copy.

Give the agent a reference video or images and a task, for example:

> Reconstruct the room from reference.mp4 in Blender. Save scene.blend and render
> a camera walkthrough. Compare the renders with the reference, inspect unclear
> regions with magnify, and refine the scene.

| Setting | Effect |
| --- | --- |
| `localEditScope` | Focus each edit on one visual discrepancy while keeping the whole-scene requirements. |
| `magnify` | Crop an existing reference or render for closer inspection; no new detail is generated. |
| `awaitRender` | Wait for render/build results when there is no independent work, reducing polling-only turns. |

All switches default to `false`. They only take effect in a trusted project;
restart Pi after changing them. Settings stay in `solpi-visual.json`, separate
from the base `sol-pi.json`. Crop files are stored under Pi's session directory
in `sol-pi-examples/solpi-visual/`; temporary sessions use a private temp directory.

A `magnify` call uses pixel coordinates `[left, top, right, bottom]`:

```json
{"image":"renders/front.png","bbox":[120,80,260,240],"scale":2}
```

For paired inspection, add `reference` and `referenceBbox`. Inputs must be PNG/JPEG;
the default output edge limit is 1024 pixels. Source images are left unchanged.

## 15-scene results

Model: **GPT-6 Astra**, high reasoning effort. The comparison uses 15 scenes:
five each from ARKitScenes, ScanNet++ and ScanNet, selected from
[VSI-Bench](https://huggingface.co/datasets/nyu-visionx/VSI-Bench).

| Method | Mean visual score ↑ | Recorded fee / scene ↓ | Calls / scene ↓ |
| --- | ---: | ---: | ---: |
| Codex | 76.87 | 8.95 | 71.53 |
| SoL-Pi | 75.80 | 9.53 | 100.53 |
| SoL-Pi Visual | 70.35 | 5.60 | 62.00 |

Selected experiment snapshots, including recovery outputs; scores are model-graded
and fees are recorded subtotals. These experiments were not rerun for this example.

![Aggregate results and visual scores for all 15 scenes](https://huggingface.co/datasets/Belta/solpi-visual-preview/resolve/310acc1042ce4a925053700a7b4b5f76bf9aba14/results.png)

The figure is about **72 KiB**, hosted on Hugging Face. [Per-scene results](https://huggingface.co/datasets/Belta/solpi-visual-preview/resolve/310acc1042ce4a925053700a7b4b5f76bf9aba14/full15.json)
and [CSV](https://huggingface.co/datasets/Belta/solpi-visual-preview/resolve/310acc1042ce4a925053700a7b4b5f76bf9aba14/full15.csv) are available there too.

The 45 reference/Codex/SoL-Pi videos remain in the private
[Belta/solpi-visual dataset](https://huggingface.co/datasets/Belta/solpi-visual),
which requires authorized access. Reference clips use the first 30 seconds;
reconstruction videos are Blender exports from the corresponding experiments.
