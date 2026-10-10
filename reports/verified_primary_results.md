# Verified summary of the four frozen primary results (checked against results_multigroup.json and hashes on 2026-10-09)

| Group | n | Delta R2 | 95% CI | p (perm) | p (BH) | Classification |
|---|---|---|---|---|---|---|
| DL | 66 | -0.056 | [-0.176, +0.057] | 0.521 | 0.695 | NO_DETECTABLE_GAIN |
| WR | 59 | -0.018 | [-0.054, +0.016] | 0.498 | 0.695 | NO_DETECTABLE_GAIN |
| OL | 66 | +0.010 | [-0.051, +0.078] | 0.695 | 0.695 | NO_DETECTABLE_GAIN |
| DB | 62 | -0.016 | [-0.046, +0.010] | 0.643 | 0.695 | NO_DETECTABLE_GAIN |

Interpretation: no detectable incremental out-of-sample value under the tested design (4 coarse cross-drill composites, ~60 players/group, 3 draft classes, leave-one-class-out). This does not show that all tracking features are useless.
Frozen file hashes (results_dl.json, run_analysis_dl.py, analysis_plan.md, multigroup_analysis_plan.md) verified unchanged.
