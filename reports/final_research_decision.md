# Final research decision (Phase 4) — written 2026-10-09 before any further analysis
Inputs: verified_primary_results.md (frozen), literature_review.md, novelty_matrix.md, power_followup.json (synthetic, outcome-free). **No new association with an NFL outcome was computed in this stage.**

## 1. Was one more drill-specific test justified? Decision: **No. None run; no new plan written.**
The rule was: run one only if (i) the literature shows a real gap, (ii) the measurement is valid and reliable, (iii) n makes it informative. Two candidates were assessed.

| | H1: DL pass-rush-drill early-phase burst/braking -> adjusted get-off | H2: WR deceleration into route breaks -> adjusted separation |
|---|---|---|
| Football rationale | First-step quickness should show in pass-rush get-off | Braking into the break should create separation |
| (i) Gap? | **No.** First-step/burst-to-pressure for DL was already probed in public repos (bansal1600: shuttle->burst->pressure n=25; ashwin: IDL/EDGE first-second accel, later partly retracted; hoop-drill bend null). Our own frozen DL composites were null. | **No.** Route-break mechanics were explored by bansal1600 (38 of 43 pairs |rho|<0.25), ashwin ("route break -> separation-over-expected: null, drop"), and planned by Kenjaro70. |
| (ii) Valid, reliable measurement? | **Weak.** PASS_RUSH_DRILL retest (Spearman-Brown): peak accel 0.33, brake 0.37, turn 0.33 (peak speed 0.77). Early-phase features also need motion-onset detection, which was noisy for the 40 (tracked 10-yd split retest 0.45). | **Not for the matching drills.** Route drills with >=2 attempts are rare: POST_CORNER_ROUTE_RIGHT brake 0.23 (n=15), SPEED_OUT_ROUTE_LEFT brake 0.03 (n=17); most route drills have one attempt (reliability not estimable). Only GAUNTLET brake is reliable (0.76, n=93) but it is not a route-break drill, so it would not test the stated hypothesis. |
| (iii) Informative? | 58 of 66 DL have >=2 attempts. Simulation (n=66, one added feature, LOCO permutation test): power for true incremental R^2 0.05 / 0.10 = 24% / 23% at reliability 0.4; 35% / 61% at reliability 0.8. False-positive rate 3-7%. | 57 of 63 WR have >=2 GAUNTLET attempts; same power limits; hypothesis mismatch. |
| Forking-path risk | A fifth test after four nulls, chosen with knowledge of them, would be a follow-up that cannot restore confirmatory status; a single p-value from it would be weakly interpretable. | Same. |
**Conclusion:** the gaps are not real, the measurement is weak or mismatched, and the test would be underpowered. Running it would mostly add a fifth null or a fragile positive. In keeping with your rule, no test was run "simply to obtain a positive result." If a test is ever reconsidered it needs: a drill feature with retest >=0.8 in >=60 players, a matched in-game phase, an outcome with reliability >=0.7, and a new hashed plan written first.

## 2. Path comparison
**A.** Four-position map of tracking reliability, redundancy and incremental predictive value (frozen results; no further hypothesis test).
**B.** Path A + one drill-specific investigation (H1 or H2).

| Criterion | Path A | Path B |
|---|---|---|
| Novelty | Low-moderate. The *topic* is crowded (>=2 detailed public entries on reliability/translation nulls; one already has nested out-of-sample models). Distinct only in design rigor (pre-registration, held-out classes, bounded effects, outcome-side reliability, detectability analysis). | Not higher: the added hypotheses duplicate public probes; a positive would be fragile and unreplicated. |
| Statistical credibility | High: plans hashed before analysis, one confirmatory family, BH, CIs vs practical threshold, anchor frozen, all post hoc labelled. | Lower: a post-null follow-up, low power (24-61%), multiplicity ambiguity, and the main story would hinge on one result. |
| Football insight | Moderate: tells scouts which numbers add nothing detectable over stopwatch/size/draft, which are unreliable, and what would need to be true for tracking to help. Weakness: findings are mostly "no detectable gain". | Small incremental insight at best; a fragile result could mislead. |
| Feasibility / risk | Done or nearly done; word and figure budget (2,000 words, <10 tables/figures) fits a clear story. | Extra analysis, plan, tests, and explanation consume word budget; higher chance of an unclear headline. |
**Recommendation: Path A.** It is stronger because its credibility rests on design and inference, which Path B would dilute with an underpowered, post-null add-on; and because the only truly open space in this competition is rigor and bounded, actionable interpretation, not a fifth exploratory transfer test.

## 3. Risks of Path A that must be managed (not hidden)
1. **Crowding:** judges may read several "nothing transfers" entries. Differentiators must be the pre-registered held-out design, effect bounds, and detectability analysis, presented concisely; do not claim novelty for the sprint-model/redundancy findings that competitors also report.
2. **Weak Football novelty score:** counter with scout-usable content that our evidence actually supports (see next step), not with positive-sounding spin.
3. **Not proof of absence:** all language must stay "no detectable incremental out-of-sample gain under this design"; ~60 players per group, three classes, 4 coarse composites, many single-attempt drills.
4. **Moving target:** re-scan public entries before submission.

## 4. Exact next step
1. **Verify Rules (manual):** submission count (earlier snippet: up to 2; third-party repos: one per team), winner license/OSI-dependency terms, data-security clause, external-data policy, and Open vs University track; paste the relevant text.
2. **Outcome-free measurement report** from existing data (no new outcome test): per drill x feature x group retest reliability with CIs, Spearman-Brown reps needed, minimum detectable difference, and redundancy with stopwatch/size. Flag its overlap with ashwinsreedhar28's report card in the writeup.
3. **Re-scan public entries** around late December and again just before Jan 6 2027.
4. Only then build the notebook (Kaggle-path, fresh-kernel run, <10 tables+figures combined) and the <=2,000-word writeup, with a claims-to-evidence checklist tied to results_multigroup.json.
