# Novelty matrix: closest existing work vs our project (as of 2026-10-09; competitor repos are moving targets)
Legend: [P] peer-reviewed, [C] competition public repo (claims unverified). "Not stated" = I did not see it, not that it is absent.

| Dimension | LaPlaca & McCullick 2020 [P] | bansal1600 "Measure the Athlete" [C] | ashwinsreedhar28 "What sensors add, and don't" [C] | **Our project** |
|---|---|---|---|---|
| Research question | Which Combine tests correlate with NFL performance, by position | Which Combine sensor traits are repeatable, translate to same trait in NFL snaps, and relate to production | Which sensor measurements are reliable and add anything beyond stopwatch/draft slot for NFL movement or production | Do Combine-tracking composites add out-of-sample information beyond conventional measures, by position, under a pre-specified design |
| Population / positions | All offensive & defensive positions; stopwatch-era classes | 510 prospects, 5 groups; n=25-79 per test | 510 prospects, all groups; n=22-74 per cell | DL 66, WR 59, OL 66, DB 62 (>=100 snaps); TE excluded (n=21 eligible) |
| Tracking-derived measures | None (stopwatch/tape) | Top speed, burst, brake, bend from SavGol derivatives of x/y; same code on Combine and NFL snaps | Per-drill kinematics, mono-exponential 40 fit (vmax, tau, v10/v20), DB-transition features | 4 cross-drill composites (peak speed/accel/brake, max turn rate) from x/y derivatives; 40-yard sprint model (reliability/redundancy check only) |
| Outcome definition | Position-specific NFL statistics/indicators | Same-trait NFL movement (90th pct of snap maxima) + production rates (pressure, etc.) | In-game top speed/accel/COD, pressure rate, YAC-over-expected, separation-over-expected, career snaps | Role/context-adjusted EB player effects: DL get-off, WR separation, OL pressure allowed vs expected, DB in-game top speed (physical only); DB coverage production blocked |
| Reliability assessment | Not stated in abstract | Retest, cross-drill agreement, NFL split-half, Spearman-Brown, reps-needed table | ICC with bootstrap CIs, SB reps-needed, SEM/MDD, report card | Retest SB per drill x feature (est. only for multi-attempt drills), **plus outcome-side split-half by game parity**, redundancy R^2 vs stopwatch/size |
| Statistical design / validation | Spearman at p<=.05/.01, many tests | Partial Spearman (weight, position, draft yr), family-wise permutation max-|rho| test, bootstrap CIs; no held-out class | Partial-correlation screen (4,637 tests, BH-FDR), nested leave-one-out R^2 models, player-level OLS (HC3); retractions logged | **Plan written and hashed before analysis; leave-one-draft-class-out predictions; paired baseline vs enhanced on identical players; permutation test + BH across 4 groups; pre-set practical threshold (+0.10 R^2) and classification rules; frozen DL anchor** |
| Principal findings (as claimed) | At least one test per position correlates | Tracked 40 speed travels (WR); position-drill COD traits unreliable; 0/144 translations survive FWER; DL shuttle -> burst (n=25) | 40 = top-speed test; most position drills unreliable; sensor adds ~0 over stopwatch for in-game movement; OL nothing | No detectable gain from tracking composites in any group (CIs exclude >=+0.10 for all four); conventional measures predict WR separation (R^2 0.34) but tracking adds nothing; OL outcome noisy (split-half 0.40) |
| Practical scouting implication | Use tests as correlates | Use tracked 40 peak speed; discount single position-drill reps; standardize drills; use NFL tracking once available | Trust the few reliable drills; use report card, reps needed, MDD | (not yet drafted) candidate: which numbers to trust, how much a tracking number could add at most, what to standardize |
| **Genuinely distinct contribution?** | - | - | - | **Design/inference rigor only** (see below) |

## Overlap that we must not claim as ours
Sprint-model finding that sensor vmax ~ stopwatch 40 (r about -0.95/-0.965 in both our work and ashwin's); tau being unreliable (0.36 vs their 0.34); position-drill unreliability; "sensor adds nothing beyond stopwatch" for in-game movement; nulls for OL pass protection and WR separation. These are **independent convergent results**, which strengthens credibility but are not novel.

## What is plausibly distinct (honest assessment)
1. **Pre-specification and auditability**: hashed plans dated before computation, a plan-hash check in the script, a frozen anchor, and labelled post hoc analyses. Competitors' logs show exploratory screens and retractions; ours is a different epistemic standard, not a different finding.
2. **Held-out draft-class validation** with a paired baseline-vs-enhanced comparison on identical players, rather than in-sample partial correlations or leave-one-out.
3. **Bounding the effect** (CI upper bounds vs a pre-set practical threshold) and a **detectability analysis** (power simulation: single reliable feature with true incremental R^2 0.10 detected ~61% of the time at n=66; ~23% at reliability 0.4) that explains how much a null can and cannot rule out.
4. **Outcome-side reliability** reported next to predictor reliability (e.g., OL pressure-allowed split-half 0.40 limits any predictor).
5. Role/context-adjusted football outcomes for WR separation and OL pressure allowed vs expected. *Partial overlap:* ashwin's repo also builds separation-over-expected and reports OL nulls.
**None of these is a new football discovery.** They address the rubric's Data Science (30%) and Writeup/Viz criteria better than Football-novelty (30%).

## Unresolved novelty risks
- Competitors may publish a nested out-of-sample comparison and report card first; at least one already has them.
- I did not read three other repos' methods.
- Our own early lesson (tracking top speed is redundant with the stopwatch 40) is already public.
