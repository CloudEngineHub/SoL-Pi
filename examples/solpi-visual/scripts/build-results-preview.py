#!/usr/bin/env python3
"""Build a local historical-results preview without running a new experiment."""
import argparse
import hashlib
import html
import json
import math
import shutil
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE_METHODS = ["codex", "solpi", "visual", "visual_await"]
METHODS = ["codex", "solpi", "visual_await"]
LABELS = ["Codex", "SoL-Pi", "SoL-Pi Visual"]
COLORS = ["#526477", "#428b86", "#76a52d"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def public_page(out):
    """Public-facing artifact: charts and source links, with no third-party media."""
    catalog = json.loads((ROOT / "results/video-sources.json").read_text())
    sources = {
        "ARKitScenes": "https://github.com/apple-aiml-research/ARKitScenes",
        "ScanNet++": "https://scannetpp.mlsg.cit.tum.de/scannetpp/",
        "ScanNet": "https://www.scan-net.org/",
    }
    assert len(catalog["scenes"]) == 15
    rows = "".join(
        f'<tr><td>{html.escape(s["scene"])}</td><td><a href="{sources[s["dataset"]]}">{html.escape(s["dataset"])}</a></td><td>{html.escape(s["source_id"])}</td></tr>'
        for s in catalog["scenes"]
    )
    page = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>SoL-Pi Visual · Results</title><style>body{{font:16px/1.6 system-ui,sans-serif;color:#223438;background:#f6f8f7;margin:0}}main{{max-width:1200px;margin:auto;padding:32px 20px}}article{{background:white;padding:24px;margin:24px 0;border:1px solid #dde5e0;border-radius:12px}}img{{width:100%;height:auto}}table{{width:100%;border-collapse:collapse}}td,th{{text-align:left;border-bottom:1px solid #ddd;padding:8px}}a{{color:#487914}}nav{{display:flex;gap:24px;flex-wrap:wrap}}.small{{font-size:14px;color:#647176}}</style>
<main><p>SoL-Pi Visual · Example</p><h1>Scene Reconstruction Results</h1>
<p>SoL-Pi Visual is an experimental example exploring visual scene reconstruction with SoL-Pi.</p>
<p><strong>Model:</strong> GPT-6 Astra (<code>gpt-6-astra</code>), with high reasoning effort.</p>
<nav><a href="#full15">15-scene comparison</a><a href="#sources">Source scenes</a></nav>
<article id="full15"><h2>15 Scenes · Three Methods</h2><img src="overview.svg" alt="Mean score, known fee and calls"><img src="scene-scores.svg" alt="Horizontal score heatmap for 15 scenes"></article>
<article id="sources"><h2>15 Source Scenes</h2><p>Reference clips came from <a href="https://huggingface.co/datasets/nyu-visionx/VSI-Bench">VSI-Bench</a>, using the first 30 seconds. Videos and extracted frames are not redistributed in this public package. Obtain source data through the dataset owners under their terms.</p><table><tr><th>Scene</th><th>Original dataset</th><th>Scene ID</th></tr>{rows}</table></article>
<p class="small">Result data: <a href="results/full15.json">15-scene results</a> · <a href="PUBLICATION_MANIFEST.json">File manifest</a></p></main></html>'''
    (out / "index.html").write_text(page)
    entries = [{"path": str(p.relative_to(out)), "sha256": sha(p)} for p in sorted(out.rglob("*")) if p.is_file()]
    (out / "PUBLICATION_MANIFEST.json").write_text(json.dumps({"scope": "charts, numeric results and source links only; no video, reference frames, crop images or remote media embeds", "scenes": 15, "files": entries}, indent=2) + "\n")


def main():
    if not __debug__:
        raise RuntimeError("Do not use python -O: preview integrity checks must remain enabled")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full15-root", type=Path)
    parser.add_argument("--public", action="store_true", help="Build charts and source links only, without copying any media")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.public and args.full15_root is None:
        parser.error("the private preview requires --full15-root")
    out = (args.output or ROOT / ("output/public-preview" if args.public else "output/review-preview")).resolve()
    if args.public and out.exists() and (not out.is_dir() or any(out.iterdir())):
        parser.error("public output must be empty; use a new directory to avoid including stale private media")
    out.mkdir(parents=True, exist_ok=True)
    # Keep the generated preview self-contained, including its provenance links.
    (out / "results").mkdir(exist_ok=True)
    for name in ["full15.json", "full15.csv", "video-sources.json"] + ([] if args.public else ["media.json"]):
        shutil.copyfile(ROOT / "results" / name, out / "results" / name)
    full = json.loads((ROOT / "results/full15.json").read_text())
    if not args.public:
        snapshot = args.full15_root / "reported-snapshots/full15_product_comparison_20260930T083601Z"
        assert sha(snapshot / "SUMMARY.json") == full["source_sha256"]
        selection = json.loads((snapshot / "CURRENT_COMPARISON.json").read_text())
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "svg.fonttype": "none"})
    aggregates = {x["method"]: x for x in full["aggregates"]}
    assert len(full["rows"]) == 60
    assert len({(x["scene"],x["method"]) for x in full["rows"]}) == 60
    for method in SOURCE_METHODS:
        selected = [x for x in full["rows"] if x["method"] == method]
        assert len(selected) == 15
        assert math.isclose(sum(x["visual_score"] for x in selected)/15, aggregates[method]["mean_visual_score"], abs_tol=1e-9)
        assert math.isclose(sum(x["known_fee"] for x in selected), aggregates[method]["selected_snapshot_known_cost"], abs_tol=1e-9)
        assert sum(x["calls"] for x in selected) == aggregates[method]["selected_snapshot_calls"]
        assert sum(x["unknown_fee_requests"] for x in selected) == aggregates[method]["selected_snapshot_unknown_cost_requests"]
    fig, axes = plt.subplots(1, 3, figsize=(13.8, 4.2), constrained_layout=True)
    for ax, key, divisor, title in zip(axes,
        ["mean_visual_score", "selected_snapshot_known_cost", "selected_snapshot_calls"],
        [1, 15, 15], ["Mean visual score", "Known fee / scene", "Calls / scene"]):
        values = [aggregates[m][key] / divisor for m in METHODS]
        bars = ax.bar(range(len(METHODS)), values, color=COLORS, width=.66)
        ax.set_xticks(range(len(METHODS)), LABELS, rotation=20, ha="right")
        ax.set_title(title, loc="left", fontweight="bold")
        ax.set_ylim(0, 100 if key == "mean_visual_score" else max(values) * 1.22)
        ax.bar_label(bars, fmt="%.2f", padding=4)
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=.15)
        ax.set_axisbelow(True)
    fig.savefig(out / "overview.svg")
    plt.close(fig)
    scenes = [f"V{i}" for i in range(1, 16)]
    lookup = {(x["scene"], x["method"]): x for x in full["rows"]}
    values = np.array([[lookup[(s, m)]["visual_score"] for s in scenes] for m in METHODS])
    fig, ax = plt.subplots(figsize=(15, 4.1), constrained_layout=True)
    image = ax.imshow(values, vmin=40, vmax=90, cmap="YlGnBu")
    ax.set_xticks(range(15), scenes)
    ax.set_yticks(range(len(METHODS)), LABELS)
    for i in range(len(METHODS)):
        for j in range(15):
            ax.text(j, i, f"{values[i,j]:.2f}", ha="center", va="center", fontsize=9,
                color="white" if values[i,j] >= 75 else "#15313a")
    ax.set_title("All 15 scene scores", pad=16, fontweight="bold")
    fig.colorbar(image, ax=ax, label="Model rubric score")
    fig.savefig(out / "scene-scores.svg")
    plt.close(fig)
    if args.public:
        public_page(out)
        print(json.dumps({"preview": str(out / "index.html"), "scope": "public-source-links", "scenes": 15, "media_files": 0}))
        return
    media = []
    for scene in scenes:
        report_info = selection["selected_reports"][scene]
        # The frozen ledger records original absolute paths; resolve against
        # the supplied archive root when rebuilding on another machine.
        report_relative = report_info["path"].split("/20260929_visual_await_full15/", 1)[1]
        report_path = args.full15_root / report_relative
        assert sha(report_path) == report_info["sha256"]
        report = json.loads(report_path.read_text())
        blind = args.full15_root / "evaluation-four-method" / ("blind-" + report_info["version"])
        manifest = json.loads((blind / "MANIFEST.json").read_text())
        evidence = report
        if scene == "V1":
            evidence = json.loads((args.full15_root / "evaluation-four-method/harmonized-results/V1/SCORES.json").read_text())
        if "source_manifest_sha256" in evidence:
            assert sha(blind / "MANIFEST.json") == evidence["source_manifest_sha256"]
        else:
            freezes = list((args.full15_root / "evaluation-four-method").glob("fresh-grader-*/FREEZE.json"))
            freeze_path = next(p for p in freezes if sha(p) == evidence["freeze_sha256"])
            freeze = json.loads(freeze_path.read_text())
            assert sha(blind / "MANIFEST.json") == freeze["source_manifest_sha256"]
            assert sha(freeze_path.parent / "FROZEN_REVIEW.json") == evidence["review_sha256"]
        if "scores" in evidence:
            label_map = {x["method"]: x["anonymous_label"] for x in evidence["scores"]}
        else:
            mapping_path = args.full15_root / "evaluation-four-method/private" / report_info["version"] / "MAPPING.json"
            if "mapping_sha256" in evidence:
                assert sha(mapping_path) == evidence["mapping_sha256"]
            label_map = {method: label for label, method in json.loads(mapping_path.read_text()).items()}
        assert set(label_map) == set(SOURCE_METHODS) and len(set(label_map.values())) == 4
        # Cross-check the mapping against the frozen rubric totals as well.
        freezes = list((args.full15_root / "evaluation-four-method").glob("fresh-grader-*/FREEZE.json"))
        freeze_path = next(p for p in freezes if sha(p) == evidence["freeze_sha256"])
        review_path = freeze_path.parent / "FROZEN_REVIEW.json"
        assert sha(review_path) == evidence["review_sha256"]
        review = json.loads(review_path.read_text())
        for method, label in label_map.items():
            scored = next(x for x in review["labels"] if x["label"] == label)
            total = sum(x["rating"] * x["weight"] for x in scored["criteria"])
            assert math.isclose(total, lookup[(scene, method)]["visual_score"])
        for view in [1, 4]:
            for method, label in [("reference", "Reference")] + [(m, dict(zip(METHODS, LABELS)).get(m, "Archived ablation")) for m in SOURCE_METHODS]:
                entries = manifest["reference"] if method == "reference" else manifest["labels"][label_map[method]]["views"]
                entry = next(x for x in entries if x["view"] == view)
                source = blind / entry["path"]
                assert sha(source) == entry["sha256"]
                relative = f"media/{scene}/{method}-view-{view:02d}.png"
                target = out / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
                media.append({"path":relative, "source_study":full["study"], "source_path":str(source.relative_to(args.full15_root)), "sha256":entry["sha256"], "scene":scene, "method":method, "view":view, "source_seconds":entry["source_seconds"], "selected_report_sha256":report_info["sha256"]})
    video_sections = []
    videos = []
    source_catalog = json.loads((ROOT / "results/video-sources.json").read_text())
    source_by_scene = {x["scene"]: x for x in source_catalog["scenes"]}
    assert set(source_by_scene) == set(scenes)
    video_index = ROOT / "results/media.json"
    if video_index.exists():
        videos = json.loads(video_index.read_text())["files"]
        assert len(videos) == 45
        assert {(x["scene"], x["method"]) for x in videos} == {(s, m) for s in scenes for m in ["reference", "codex", "solpi"]}
        for scene in scenes:
            cells = []
            for method, label in [("reference", "Reference"), ("codex", "Codex"), ("solpi", "SoL-Pi")]:
                entry = next(x for x in videos if x["scene"] == scene and x["method"] == method)
                path = entry["path"]
                assert sha(out / path) == entry["sha256"]
                cells.append(f'<figure><video controls playsinline preload="none" poster="media/{scene}/{method}-view-01.png" src="{path}"></video><figcaption>{label} · {entry["width"]}×{entry["height"]} · {entry["duration_seconds"]:.1f}s</figcaption></figure>')
            hidden = "" if scene == "V1" else " hidden"
            origin = source_by_scene[scene]
            video_sections.append(f'<section data-video-scene="{scene}"{hidden}><h3>{scene} · {html.escape(origin["dataset"])} · {html.escape(origin["source_id"])}</h3><div class="videos">'+"".join(cells)+'</div></section>')
    rows = "".join(f'<tr><td>{s}</td>'+"".join(f'<td>{lookup[(s,m)]["visual_score"]:.2f}</td>' for m in METHODS)+"</tr>" for s in scenes)
    aggregate_rows = "".join(f'<tr><td>{label}</td><td>{aggregates[m]["mean_visual_score"]:.4f}</td><td>{aggregates[m]["selected_snapshot_known_cost"]:.6f}</td><td>{aggregates[m]["selected_snapshot_calls"]}</td></tr>' for m,label in zip(METHODS,LABELS))
    source_rows = ''.join(f'<tr><td>{s}</td><td>{html.escape(source_by_scene[s]["dataset"])}</td><td><code>{html.escape(source_by_scene[s]["source_id"])}</code></td></tr>' for s in scenes)
    scene_options = ''.join(f'<option>{s}</option>' for s in scenes)
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>SoL-Pi Visual · Results</title>
<style>CSS</style>
<main><div class="tag">SoL-Pi Visual · Example</div>
<h1>Scene Reconstruction Results</h1>
<p>SoL-Pi Visual is an experimental example exploring visual scene reconstruction with SoL-Pi.</p>
<p><strong>Model:</strong> GPT-6 Astra (<code>gpt-6-astra</code>), with high reasoning effort.</p>
<nav><a href="#full15">15-scene comparison</a><a href="#videos">Scene videos</a></nav>
<p class="note">These results include preserved failed snapshots and mechanical recovery outputs; they do not establish original end-to-end success. Fees are known subtotals up to the scored snapshots, with missing records and unverified currency. No new scene experiment was run for this example.</p>
<article id="full15"><h2>15 Scenes · Three Methods</h2>
<img class="chart" src="overview.svg" alt="Mean score, known fee and calls across 15 scenes">
<div class="scroll"><table><tr><th>Method</th><th>Mean visual score</th><th>Total known fee</th><th>Calls</th></tr>AGGREGATE</table></div>
<img class="chart heatmap" src="scene-scores.svg" alt="Scores for all 15 scenes across three methods">
<details><summary>Show all scene scores</summary><div class="scroll"><table><tr><th>Scene</th><th>Codex</th><th>SoL-Pi</th><th>SoL-Pi Visual</th></tr>SCENE_ROWS</table></div></details></article>
<article id="videos"><h2>15 Scenes · Video Results</h2>
<p>Reference clips: the first 30 seconds of 15 <a href="https://huggingface.co/datasets/nyu-visionx/VSI-Bench">VSI-Bench</a> scenes, five each from ARKitScenes, ScanNet++ and ScanNet. Reconstruction videos: Blender renders from Codex and original SoL-Pi.</p>
<details><summary>Show original datasets and scene IDs</summary><table><tr><th>Scene</th><th>Original dataset</th><th>Original scene ID</th></tr>SOURCE_ROWS</table><p class="small">This is a reconstruction study using selected videos, not the official VSI-Bench question-answering evaluation. See <a href="results/video-sources.json">video-sources.json</a> for the source index.</p></details>
<label for="scene-picker">Select scene </label><select id="scene-picker">SCENE_OPTIONS</select>VIDEO_SECTIONS</article>
<p class="small">Result data: results/full15.json. Media and chart checksums: <a href="VISUALIZATION_MANIFEST.json">visualization manifest</a>.</p>
<script>document.getElementById('scene-picker').addEventListener('change', event => {document.querySelectorAll('[data-video-scene]').forEach(section => {section.querySelectorAll('video').forEach(video => video.pause());section.hidden = section.dataset.videoScene !== event.target.value;});});</script>
</main></html>'''
    for key, value in {"CSS":'*{box-sizing:border-box}body{font:16px/1.65 system-ui,sans-serif;margin:0;color:#223438;background:#f6f8f7}main{max-width:1360px;margin:auto;padding:40px 28px}h1{font-size:36px;line-height:1.3;margin:10px 0}h2{margin-top:0}h3{margin-bottom:8px}a{color:#487914}nav{display:flex;gap:22px;flex-wrap:wrap;margin:22px 0}.tag{color:#548124;font-weight:650}.note{padding:14px 18px;background:#f0f4e8;border-left:4px solid #76a52d;border-radius:4px}.small{font-size:13px;color:#647176}article{background:white;border:1px solid #dde5e0;border-radius:14px;padding:28px;margin:24px 0}.chart{display:block;width:100%;height:auto;margin:20px auto}.heatmap{max-width:1320px}table{border-collapse:collapse;width:100%;font-size:14px}th,td{text-align:left;padding:9px 12px;border-bottom:1px solid #e7ece9}th{background:#f5f7f5}section{margin-top:25px}.scroll{overflow:auto}@media(max-width:850px){main{padding:24px 14px}article{padding:18px}h1{font-size:28px}} .videos{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.videos figure{margin:0}.videos video{width:100%;aspect-ratio:16/9;object-fit:contain;background:#182321;border-radius:8px}.videos figcaption{font-size:13px}select{font:inherit;padding:6px 28px 6px 10px;border:1px solid #b6c8ba;border-radius:6px;background:white}[hidden]{display:none!important}@media(max-width:850px){.videos{grid-template-columns:1fr}}',"AGGREGATE":aggregate_rows,"SCENE_ROWS":rows,"SOURCE_ROWS":source_rows,"SCENE_OPTIONS":scene_options,"VIDEO_SECTIONS":"".join(video_sections)}.items():
        page = page.replace(key, value)
    (out / "index.html").write_text(page)
    (out / "VISUALIZATION_MANIFEST.json").write_text(json.dumps({"display_methods":dict(zip(METHODS,LABELS)),"archived_ablation":"visual","full15_source_sha256":full["source_sha256"],"images":media,"videos":videos,"generated_charts":[{"path":name,"sha256":sha(out/name)} for name in ["overview.svg","scene-scores.svg"]]},indent=2)+"\n")
    print(json.dumps({"preview":str(out/"index.html"),"historical_rows":len(full["rows"]),"copied_images":len(media),"media_bytes":sum((out/x["path"]).stat().st_size for x in media)}))


if __name__ == "__main__":
    main()
