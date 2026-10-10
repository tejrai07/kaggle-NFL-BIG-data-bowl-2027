# Multi-group pre-specified analysis plan
Written 2026-10-09 **before any new Combine-tracking vs NFL-outcome association was computed** (WR, OL, DB). Hash recorded in reports/plan_hashes.txt; the analysis script verifies it.
Before this plan I looked only at outcome-free facts: drill coverage by position, available DB fields, snap counts per player (from the earlier planning step), and DL results (frozen).

## 0. Frozen DL anchor
DL get-off analysis (reports/analysis_plan.md, scripts/run_analysis_dl.py, reports/results_dl.json) is FROZEN; sha256 in /home/claude/data/frozen_hashes.txt is re-checked at the end.
New work on DL is limited to (a) computing a permutation p-value for the SAME frozen design (fixed ridge lambda=10, 11-variable baseline, same player table) so DL can enter the multiple-testing family, and (b) a labelled supplementary re-evaluation with the harmonized estimator (section 5). Neither replaces the frozen conclusion.

## 1. Common design (all groups)
- Data: regular season only (games.season_type == "REG"), play_nullified_by_penalty != "Y". Combine group = combine_results.combine_position.
- Player eligibility: >= 100 qualifying outcome snaps (sensitivity: 50, 200). Combine tracking eligibility: see section 2. Same player set for baseline and enhanced models.
- Outcome (player level): snap-level adjustment for role/context -> player mean residual -> empirical-Bayes shrinkage (same method as DL: pooled within-player variance, method-of-moments tau^2). Oriented so HIGHER = BETTER/FASTER. Outcome reliability also reported by odd/even-game split-half (Spearman-Brown), because the EB formula ignores game/team clustering.
- Tracking predictors (4 composites, fixed in advance, identical definitions to DL): peak_speed, peak_accel (peak longitudinal acceleration), peak_brake (most negative longitudinal acceleration while speed>1 yd/s), max_turn_rate (rad/s while speed>1 yd/s); computed from x,y at 10 Hz (3-frame smoothing, edge frames trimmed; the provided `a` is NOT used). Per attempt -> mean over attempts per drill -> z-score within drill (within Combine group) -> mean over the group's eligible drills.
- Eligible drills: harmonized drill names (LINE->LINE_DRILL, PASS_PRO-MIRROR_DRILL->PASS_PRO_MIRROR_DRILL, SPEED_OUT_LEFT->SPEED_OUT_ROUTE_LEFT, OVER_THE_SHOULDER_ADJUST->OVER_SHOULDER_ADJUST) with attempts for >= 80% of the group's Combine players. Player needs >= ceil(2/3 x #eligible drills) drills. (z-scoring uses only Combine tracking, no outcomes.)
- Conventional baseline (primary): forty, ten_yd_split, three_cone, short_shuttle, vertical, broad_jump, combine_height, combine_weight, arm_length, wing_span, log(draft_overall_pick; UDFA=260); training-fold median imputation + missing indicators + standardization. Bench reps excluded (62% missing). Enhanced = baseline + 4 composites.
- Model: ridge regression. Lambda chosen by inner 5-fold CV (random folds over training players, fixed seed, same folds for baseline and enhanced) over {1,3,10,30,100,300} -- applied identically to both models. (DL frozen design used fixed lambda=10.)
- Validation: leave-one-draft-class-out (train two classes, predict the third); pooled out-of-sample R^2 using the overall outcome mean as reference (as in the frozen DL code). Players never appear in both train and test. Limitation: only 3 classes; later classes have shorter exposure.
- Primary estimand per group: Delta R^2 = R^2_oos(enhanced) - R^2_oos(baseline), same eligible players.
- Uncertainty: 95% percentile CI from 5,000 player-level bootstraps of the fixed LOCO predictions (approximation: models are not refit). 
- Test (one-sided, H1: Delta > 0): permutation p-value = (1+#{Delta_perm >= Delta_obs})/(1+1000), shuffling the 4 tracking composites across players (outcome and conventional variables fixed), re-running the full LOCO enhanced pipeline each time; baseline predictions fixed.

## 2. Group definitions
### WR (Combine WR, n=107)
- Qualifying snaps: route_ran and separation_at_pass_forward non-null (denominator = routes with measured separation; not conditional on target).
- Outcome: separation_at_pass_forward (yards; higher = better). Snap-level adjustment: route_ran (categorical), lined_up_position (WR/SLOT_WR/TE/other), team_coverage_man_zone, cushion (median-imputed + missing flag), season. NOT adjusted for pass_length/yards (post-throw outcomes).
- Drills: eligible per section 1 (expected 12).
### OL (Combine OL, n=121)
- Qualifying snaps: dropbacks (pass_result non-null) with pressure_allowed non-null; denominator = all such pass-block snaps (includes snaps with no rusher encountered).
- Outcome: pressure_allowed (binary). Snap-level logistic regression (IRLS) on lined_up_position (T/G/C), down, yards_to_go (capped 20), offense_formation, team_coverage_man_zone, season; player mean residual (observed - predicted), EB-shrunk, sign flipped so higher = fewer pressures allowed. NOT adjusted for pass_rushers_encountered or dropback_duration (post-snap, outcome-linked).
- Caveat: pressure allowed depends on QB, scheme, teammates and opponents.
### DB (Combine DB, n=122)
- **Coverage-performance outcome: BLOCKED.** No defender-linked coverage result exists: target is true on 8 defender rows, separation_at_pass_forward non-null on 38, no completions/yards allowed per defender, and play results (yards_gained, EPA) are team outcomes confounded by 10 other players. No substitute is used for coverage performance.
- Separate pre-specified **physical-transfer** analysis (NOT coverage production): in-game peak speed during pass coverage. Qualifying snaps: dropbacks, lined_up_position in {CB, SLOT_CB, HIGH_SAFETY}, coverage_assignment_at_snap non-null, window = ball_snap to min(pass_forward, snap+3.0 s), window >= 2.0 s. Outcome: max speed in window (yd/s); adjusted for lined_up_position, man/zone, window length, season; higher = faster. Included in the family but interpretable only as physical translation of Combine movement.
- Drills: eligible per section 1 (expected 8).
### DL (anchor; frozen)
- As in reports/analysis_plan.md. 66 players, 4 composites, 11-variable baseline, fixed lambda=10.

## 3. Confirmatory family and correction
Family of 4 one-sided permutation tests on Delta R^2: DL (frozen design), WR, OL, DB-physical. Multiplicity: Benjamini-Hochberg FDR across the 4 tests, declare at adjusted p < 0.05. Nothing else is confirmatory.
**Classification rules (fixed now):**
- ADDS information: BH-adjusted p < 0.05 AND bootstrap 95% CI lower bound > 0.
- Otherwise: INCONCLUSIVE if CI upper bound >= +0.10 R^2 (a practically useful gain cannot be excluded); else NO DETECTABLE GAIN (any gain is < 0.10 R^2 under this design; this is not proof of none).
- REDUNDANCY flag (descriptive): median over the 4 composites of in-sample R^2 from regressing the composite on forty+weight+vertical >= 0.50.
- RELIABILITY flag: median Spearman-Brown test-retest across eligible multi-attempt drill x feature cells < 0.50; the share of single-attempt drills is reported (not estimable there).

## 4. Pre-specified sensitivity (non-confirmatory; reported for every group)
(a) min snaps 50 and 200; (b) parsimonious baseline (forty, combine_weight, vertical, log_pick); (c) tracking composites from best attempt rather than mean; (d) tracking-only model; (e) outcome from rookie season only (season == draft_year, min 50 snaps); (f) bootstrap-of-predictions vs permutation agreement. Sensitivity results cannot change the confirmatory classification.
Descriptive (exploratory): Spearman of each composite and conventional measure with the outcome (BH within group), partial Spearman controlling forty+weight.

## 5. Deviations from the DL method (necessary or deliberate)
1. Outcomes differ by position (continuous separation; binary pressure via logistic residuals; DB physical speed). 2. Nested lambda instead of fixed lambda=10 because a fixed lambda over-fit the 11-variable baseline in DL (post-hoc lesson); DL gets a supplementary harmonized re-evaluation. 3. Permutation p-values added (DL had only a bootstrap CI). 4. Drill-eligibility rule generalized (coverage >= 80%, >= 2/3 of drills; DL used >= 4 of 6). 5. EB variance ignores game/team clustering; split-half by game parity reported as a check.
## 6. Anything run after seeing results must be labelled EXPLORATORY/POST HOC in reports.
