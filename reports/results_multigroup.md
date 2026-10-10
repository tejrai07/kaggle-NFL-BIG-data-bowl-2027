# Multi-group results: where do Combine-tracking features add information beyond conventional measures?
All numbers come from scripts/run_multigroup.py (results_multigroup.json). The analysis plan (reports/multigroup_analysis_plan.md, sha256 in plan_hashes.txt) was fixed before any new association was computed; the script verifies the hash.
The DL get-off analysis is **frozen** (hashes re-verified after this stage); the new estimator reproduces its out-of-sample R^2 to 1e-14.

## Confirmatory family (4 one-sided permutation tests on Delta R^2, BH-adjusted)
| Group | Outcome | Players (classes) | Snaps | Conventional R^2 (LOCO) | +Tracking R^2 | Delta R^2 [95% CI] | p (perm) | p (BH) | Pre-specified class |
|---|---|---|---|---|---|---|---|---|---|
| DL (frozen design, lambda=10) | adjusted get-off | 66 (22/23/21) | 30,191 | -0.152 | -0.207 | -0.056 [-0.176, +0.057] | 0.521 | 0.695 | NO DETECTABLE GAIN |
| WR | adjusted separation at pass forward | 59 (27/18/14) | 27,380 | 0.338 | 0.320 | -0.018 [-0.054, +0.016] | 0.498 | 0.695 | NO DETECTABLE GAIN |
| OL | pressure allowed vs expected (sign flipped) | 66 (23/23/20) | 47,835 | -0.140 | -0.130 | +0.010 [-0.051, +0.078] | 0.695 | 0.695 | NO DETECTABLE GAIN |
| DB (physical transfer only) | adjusted in-game peak speed in coverage | 62 (20/27/15) | 24,809 | -0.061 | -0.077 | -0.016 [-0.046, +0.010] | 0.643 | 0.695 | NO DETECTABLE GAIN |
"NO DETECTABLE GAIN" = not significant and CI upper bound < +0.10 R^2: a practically useful gain is excluded *under this design*; it is not proof that tracking has no value. CIs are player-level bootstraps of fixed leave-one-class-out predictions (approximation; models not refit).
Supplementary (harmonized nested-lambda estimator on the DL design): baseline 0.045, +tracking 0.059, Delta +0.014 [-0.017, +0.048], permutation p 0.145 (not part of the family).

## What kind of null is it? (descriptive flags fixed in the plan)
| Group | Conventional signal? | Tracking redundant with 40/weight/vertical? (median R^2, flag >=0.5) | Tracking test-retest (median Spearman-Brown, flag <0.5; single-attempt drills) | Outcome reliability (split-half) | Reading |
|---|---|---|---|---|---|
| DL | Weak (forty, 10-yd, vertical, broad: |rho| 0.37-0.40, q=0.013; but baseline R^2 < 0) | 0.39 (not flagged; peak-speed composite is ~ -0.85 with forty) | 0.36 **flag**; 5 of 6 drills single-attempt | 0.94 (formula) | Partly redundant for speed; acceleration/braking too unreliable to judge |
| WR | **Yes** (weight rho -0.62, height -0.46; baseline R^2 0.34) | 0.05 (not redundant) | 0.72 (ok; 9 of 12 drills single-attempt) | 0.72 | Tracking is distinct and reasonably reliable but unrelated to separation once body size is known |
| OL | No (baseline R^2 < 0; only draft pick rho -0.33, q=0.11) | 0.05 | 0.36 **flag**; 5 of 6 single-attempt | **0.40** | Inconclusive in practice: noisy outcome + weakly reliable features; low power |
| DB (physical) | No (even forty rho -0.21, q=0.47) | 0.08 | 0.58 (ok; 6 of 8 single-attempt) | 0.84 | Tracking and conventional measures both fail to explain in-game coverage top speed (role/assignment likely dominates) |
No group shows tracking features that add measurable predictive information. Partial Spearman of each tracking composite with the outcome, controlling forty and weight, ranged from -0.23 to +0.15 in all groups (exploratory).

## DB blocker
**Coverage performance cannot be measured defensibly from this dataset**: target is true on 8 defender rows, separation_at_pass_forward is non-null on 38, and no completion/yards-allowed is linked to a defender. No substitute coverage outcome was used. The DB analysis above is a physical-transfer analysis only, and DB snaps were limited to dropbacks with a pass_forward and a window >= 2 s (about 10k candidate snaps excluded; the outcome is conditional on plays where a throw occurs).

## Sensitivity (pre-specified, non-confirmatory; cannot change the classification)
Delta R^2 ranged over: WR -0.079 to +0.091; OL +0.006 to +0.076; DB -0.010 to +0.041; DL -0.087 to -0.050 (full table in results_multigroup.json). Two intervals exclude zero: **WR rookie-season-only outcome (Delta -0.079 [-0.156, -0.017]; tracking *hurts*)** and **OL best-attempt composites (Delta +0.076 [+0.009, +0.169])**. These are 2 of 18 sensitivity intervals, were not part of the confirmatory family, and the OL one is not supported by the primary specification (mean-attempt Delta +0.010) or other OL sensitivities; treat as **exploratory, not a finding**.

## Interpretation limits
n ~60 players per group and 3 draft classes; class sizes and exposure differ (2025 class has one season); conventional baselines have many correlated inputs relative to n (nested ridge mitigates, does not remove this); tracking enters as 4 coarse cross-drill composites (drill- or phase-specific features were not tested and remain hypotheses); most drills have one attempt so reliability is not estimable for most cells; outcomes are role-, scheme- and QB-dependent; selection on playing time; no causal claims.
