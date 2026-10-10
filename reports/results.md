# Results so far (DL pre-registered analysis; all numbers from scripts/run_analysis_dl.py and the Stage-B scripts)

## Measurement validity
- 40-yard dash: tracking-derived 40 time vs official forty: r = 0.95 (n=381 players with both), constant offset +0.13 s (start-detection definition).
- Tracking 10-yd split vs official: r = 0.63; tracking 10-yd test-retest r = 0.45 (n=375). Onset-based splits are noisy at 10 Hz.
- Sprint-model top speed: test-retest 0.96; correlation with forty rho = -0.95 -> carries essentially the same information as the stopwatch.
- Sprint-model acceleration constant (tau): test-retest 0.36 -> not a stable trait from one attempt.
- In-game: tracking 1-second advance vs NFL `player_get_off` rho = -0.90 (33,369 DL snaps, 99.9% usable).

## Pre-registered Q1: DL get-off (n = 66 DL, 30,191 REG snaps; outcome reliability 0.94; classes 22/23/21)
- Conventional measures correlate with adjusted get-off (Spearman, BH-adjusted q ~0.013): forty -0.38, ten_yd -0.38, vertical +0.40, broad +0.37, weight -0.33.
- Tracking composites (cross-drill z-means): peak speed +0.34, peak accel +0.33, peak brake -0.37 (q ~0.013); turn rate +0.11 (n.s.).
- Out-of-sample (leave-one-class-out) R2: pre-registered 11-variable baseline -0.15 (overfit); baseline+tracking -0.21; delta -0.056, 95% CI [-0.17, +0.06].
- Tracking composites correlate with forty (peak speed rho -0.85) and weight; partial rho controlling weight+forty: speed -0.09, accel +0.13, brake -0.20, turn +0.06.
- POST HOC (not pre-registered) parsimonious baseline forty+weight: LOCO R2 0.096; + tracking(4): 0.057 (delta -0.039, CI [-0.154,+0.067]); + tracking(3): 0.090 (delta -0.006, CI [-0.086,+0.080]).
**Conclusion supported so far: for DL get-off, the tracking composites tested add no detectable incremental out-of-sample information beyond forty and weight. This is a null result.**
Caveats: n=66, three classes, bootstrap CIs hold fixed LOCO predictions (approximation), ridge penalty chosen a priori (10, 30), drills with one attempt cannot be reliability-checked.
