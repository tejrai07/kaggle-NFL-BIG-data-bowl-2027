"""Outcome-free detectability analysis for a hypothetical single-feature follow-up (see reports/final_research_decision.md).
Synthetic data only (no real outcomes): n=66 players, classes 22/23/21, 4 conventional predictors (true R2 0.10), one added feature with
true incremental R2 and measurement reliability; LOCO ridge (lambda=10), one-sided permutation test (B=150), 120 simulations per cell."""
import sys, json; sys.path.insert(0, "src")
import numpy as np, multigroup as m
rng = np.random.default_rng(7); cl = np.repeat([2023, 2024, 2025], [22, 23, 21]); n = 66
def sim(true_inc, rel, nsim=120, B=150):
    hit = 0
    for _ in range(nsim):
        xc = rng.normal(size=(n, 4)); z = rng.normal(size=n); zo = np.sqrt(rel) * z + np.sqrt(1 - rel) * rng.normal(size=n)
        y = np.sqrt(0.10 / 4) * xc.sum(1) + np.sqrt(true_inc) * z + np.sqrt(1 - 0.10 - true_inc) * rng.normal(size=n)
        pb, _ = m.loco_predict(xc, y, cl, lam=10.0); pe, _ = m.loco_predict(np.column_stack([xc, zo]), y, cl, lam=10.0); d = m.r2_oos(y, pe) - m.r2_oos(y, pb)
        ge = sum((m.r2_oos(y, m.loco_predict(np.column_stack([xc, rng.permutation(zo)]), y, cl, lam=10.0)[0]) - m.r2_oos(y, pb)) >= d for _ in range(B))
        hit += ((1 + ge) / (1 + B)) < 0.05
    return hit / nsim
out = {f"true_inc_{inc:.2f}": {f"reliability_{r}": sim(inc, r) for r in (0.4, 0.8)} for inc in (0.0, 0.03, 0.05, 0.10)}
out["note"] = "Monte-Carlo SE about +/-0.045 per cell (120 sims); non-monotone cells reflect simulation noise."
out["riley_criterion_i_n_required"] = {f"p{p}_R2_{r}": float(p / ((0.9 - 1) * np.log(1 - r / 0.9))) for p, r in [(15, 0.2), (15, 0.1), (5, 0.1)]}
json.dump(out, open("reports/power_followup.json", "w"), indent=1); print(json.dumps(out, indent=1))
