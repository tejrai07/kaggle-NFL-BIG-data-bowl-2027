# Pre-specified analysis plan (written BEFORE any Combine-feature vs NFL-outcome association was computed)
Date written: 2026-10-09. Status as of writing: only measurement-validity checks run (40-yard tracking vs stopwatch; in-game get-off vs NFL `player_get_off`).

## Primary question (Q1)
For defensive linemen (combine_position == DL), do movement features derived from Combine **position-drill tracking** explain in-game first-step
get-off beyond conventional measures (forty, ten_yd_split, 3-cone, shuttle, vertical, broad, height, weight, arm, wingspan, draft pick)?
## Secondary questions (max 2)
Q2: Does in-game get-off (adjusted) relate to pressure generation per rush snap (opportunity-controlled)?  
Q3: Which Combine measures are reliable enough to carry signal (test-retest across attempts)?

## Population / filters
DL Combine group; regular season only (games.season_type == "REG"); play_nullified_by_penalty != "Y"; snaps with non-null `player_get_off`.
Players with >= 100 such snaps are the primary sample (sensitivity: >= 50, >= 200). Preseason/playoff excluded.
## Outcome (player level)
Empirical-Bayes player effect from snap-level mixed model: get_off ~ alignment(EDGE/INTERIOR_LINE/other) + dropback + season + (1|player) [+ game random effect].
Lower get-off = faster. Report sign flipped (so higher = better) in figures. Sensitivity: tracking-derived `adv_1s` (higher = better), pass-rush snaps only.
## Features (fixed list; no outcome-driven selection)
Combine-tracking: per-drill, per-attempt kinematics from x,y (velocity from position differences, NOT the provided `a` which is a non-negative magnitude):
peak speed, peak forward/longitudinal acceleration, peak braking (negative longitudinal accel), max turn rate while speed > 1 yd/s, path length, duration.
Attempts summarized by mean over attempts (primary) and best attempt (sensitivity). Drills used must have coverage >= 80% of the DL sample after harmonizing names.
## Models and validation
1. Baseline: ridge/OLS on conventional measures (imputation within training fold only; missing-indicator for forty etc.).
2. Baseline + tracking drill features (<= 6 pre-specified composites, to be chosen from reliability and coverage, NOT outcome association).
3. Validation: leave-one-draft-class-out (train two classes, test the third) and repeated player-grouped CV. Metric: out-of-sample R2 and Spearman; delta vs baseline.
4. Uncertainty: player-level bootstrap (resample players, refit) for the delta R2; permutation test for improvement. Multiple tests: BH-FDR across screened features.
5. Confounding checks: alignment mix, weight (size proxy), draft capital/playing-time selection (players with more snaps), class/season.
## Decision rules
If delta out-of-sample R2 CI includes 0, the headline is a null/negative incremental-value finding (still reported). No new composite metric unless it beats the baseline out of sample.
## Known limits to disclose
~70-100 DL with usable snaps; 3 classes; selection into NFL playing time; get-off is a physical-outcome not production; no causal claims.
