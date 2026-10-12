# Historical scene reconstruction evidence

These are archived September 2026 pilot results, summarized on 2026-10-06.
They are **not measurements of this standalone solpi-visual 0.1.0 example**
on published npm Pi 1.0.4. The historical runs used the SIGIL experiment setup.

Source: study `20260929_visual_await_full15`,
`evaluation-supervision/FINAL15_PRODUCT_COMPARISON.md`. Each row evaluates the
same 15 scene IDs. The archived `visual` ablation combines local-edit-scope
guidance and optional Magnify. The `visual_await` arm is displayed as
**SoL-Pi Visual**; it also includes render-wait guidance.

| Method | Mean visual score ↑ | Total known fee | Known fee / scene | Calls | Requests with unknown fee |
| --- | ---: | ---: | ---: | ---: | ---: |
| Codex | 76.8667 | 134.280426 | 8.9520 | 1073 | 8 |
| Original SoL-Pi | 75.8000 | 142.898987 | 9.5266 | 1508 | 5 |
| SoL-Pi + visual | 69.1833 | 120.045183 | 8.0030 | 1283 | 27 |
| SoL-Pi + visual + await | 70.3500 | 83.967393 | 5.5978 | 930 | 14 |

Relative to original SoL-Pi, visual reduced **known** fees by 16.0% and calls by
14.9%, with a 6.62-point lower score. Adding await reduced known fees by another
30.1% and calls by 27.5%, while the score increased by 1.17 points. The combined
row is 41.2% lower in known fees than original SoL-Pi and 5.45 points lower in score.

## Limits of this comparison

- Scores include preserved failed snapshots and isolated mechanical recovery;
  they do not establish original end-to-end success. Render coverage was 60/60,
  structural pass 57/60; before current recovery, structural receipts were
  49 pass, 1 fail, 10 unassessed.
- Fees are cumulative to the scored snapshot. Later failed attempts, grading and
  infrastructure are separate; some requests lack fee records. Provider-reported
  units/currency were not independently verified. Do not label these values USD
  or total end-to-end costs.
- Reference/candidate view counts were symmetric across methods for each scene,
  but differed between scenes (35/40/45 attachments). V4 final-v3 included a
  predeclared source-only anchor and four matched candidate views.
- Scores jointly evaluate reconstruction and the native camera trajectory,
  not pure geometry under shared camera extrinsics. Conditions have single runs;
  the table is descriptive, without uncertainty estimates or causal isolation.
