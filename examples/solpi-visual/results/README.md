# Historical experiment results

This is a local import of existing September 2026 experiments, with no new
scene benchmark. The runtime example is now validated on published Pi 1.0.4.

Reconstruction model: **GPT-6 Astra** (`gpt-6-astra`), with high reasoning effort.

The table describes the full research archive. Media rows are private archive
contents, not files bundled in the code package or public preview.

| Result | Material and location | Scope |
| --- | --- | --- |
| Same 15 scenes, three displayed methods | [JSON](full15.json), [CSV](full15.csv), aggregate bars and per-scene score heatmap | Codex, original SoL-Pi and SoL-Pi Visual; the source archive preserves all 60 records |
| Scene videos | [Media index](media.json): reference + Codex + original SoL-Pi for V1–V15 | 45 existing H.264 MP4 files, about 798 MB; all original SHA-256 hashes verified |
| Archived grading frames | Reference + original experimental methods, views 1 and 4 of all 15 scenes | 150 verified PNGs retained as source material; the frame-comparison section is omitted from the preview |

See [historical-evidence.md](historical-evidence.md) for the original summary and
limitations. Fees are provider-reported known subtotals with unverified currency,
not total end-to-end spending. Scores include preserved failures and mechanical
recovery; they do not establish original task success or quality parity.

## Public preview

From this example directory, with Matplotlib and NumPy available:

```bash
python3 scripts/build-results-preview.py --public --output output/public-preview
```

Use an empty output directory. The public builder refuses nonempty destinations
so a directory containing private media cannot accidentally become a public
bundle. It uses the bundled numeric records, verifies their aggregate identities,
and includes only charts, numeric data and 15 original scene IDs/source links.
It does not require the private image/video archives or any account login.
`PUBLICATION_MANIFEST.json` lists every included file and hash. This mode checks
the bundled data; the private mode additionally checks the original frozen archives.

No reference videos, grading frames, crop demonstrations, reconstruction films
or remote media embeds are included. Third-party media permissions are therefore
not a prerequisite for this bundle. Reintroducing media requires its own permission
check, including textures or imagery incorporated into reconstruction films.

## Local preview

Open the generated `output/review-preview/index.html` locally. Charts and PNGs
stay in ignored `output/`; numerical results and the builder are separate from
runtime dependencies. Media is hosted in the private dataset
[Belta/solpi-visual](https://huggingface.co/datasets/Belta/solpi-visual).
[hosting.json](hosting.json) pins the uploaded revision. Access requires a Hugging
Face account authorized for that private repository. No token is embedded in the
page; the local preview plays downloaded files. GitHub code remains local.

The continuous videos cover the two historical baselines. SoL-Pi Visual has scored still images archived in the dataset (not displayed),
not continuous videos. All 30
baseline scene files and camera paths match the historical grading exports by
hash; the videos retain their own render settings and durations and are not the
exact grading images. No new scene experiment or scene render was run.

## Video sources

The reference clips come from the [VSI-Bench video distribution](https://huggingface.co/datasets/nyu-visionx/VSI-Bench),
with five scenes each from ARKitScenes, ScanNet++ and ScanNet. The reconstruction
study uses the first 30 seconds. [video-sources.json](video-sources.json) maps all
15 local scene IDs to their original dataset and scene IDs, and records archive
provenance where available. This is a reconstruction study using selected videos,
not the official VSI-Bench question-answering evaluation.

The Codex and original SoL-Pi films are existing Blender exports from our earlier
scene reconstruction runs, rendered along each result's own camera trajectory.
The original delivery was verified on 2026-09-27; this packaging task reuses
those files and checks them against that delivery's SHA-256 manifest.

The pinned HF revision contains the current 15-scene page, two charts, videos,
and source frames. It also includes `public-preview/`, a separate bundle with
only numeric charts, results and source links. The repository remains private.

To download the media, use Python with `huggingface_hub` installed
and an existing authorized local login, from this example directory:

```python
import json
from huggingface_hub import snapshot_download

hosting = json.load(open("results/hosting.json"))
snapshot_download(
    repo_id=hosting["repo_id"], repo_type="dataset",
    revision=hosting["revision"], local_dir="output/review-preview",
    allow_patterns=hosting["download_allow_patterns"],
)
```

Serve the downloaded preview from this example directory:

```bash
python3 -m http.server 8000 --directory output/review-preview
```

Open `http://localhost:8000`. Downloading and viewing the hosted page does not
require the original experiment archives.

To rebuild from the original source archive instead, use a Python environment
with Matplotlib and NumPy, from this example:

```bash
python3 scripts/build-results-preview.py \
  --full15-root /path/to/20260929_visual_await_full15
```

The 15-scene source archive is required for rebuilding; it is not bundled with
the code or media dataset. After rebuilding, serve `output/review-preview`
locally and open its `index.html`.

The script checks the frozen source-summary hashes, aggregate identities,
selected score-report hashes and original image hashes. It copies existing
images and plots existing numbers; it does not render scenes or call a model.
`VISUALIZATION_MANIFEST.json` in the preview records the selected media and chart
hashes. When rebuilding with `media.json` present, the 45 videos must already be
downloaded to the output directory; the builder verifies their hashes as well.

## Display naming

The preview displays `codex`, `solpi` and `visual_await` as Codex, SoL-Pi and
**SoL-Pi Visual**. The last is the complete profile including render-wait guidance.
The earlier `visual` ablation remains in the historical source archive but is not
a separate chart or table entry. No rows are merged and no scores or fees
are recomputed across different arms.

## Media reuse

The code license does not cover third-party reference clips or extracted frames.
Source attribution is recorded in `video-sources.json`; permission for public
redistribution of the selected media has not been established in this package.
In particular, consult the [ScanNet++ terms](https://scannetpp.mlsg.cit.tum.de/scannetpp/static/scannetpp-terms-of-use.pdf).
Keep the media private while the applicable source permissions are checked.
