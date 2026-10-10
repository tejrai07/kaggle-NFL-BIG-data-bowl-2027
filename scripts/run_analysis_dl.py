"""Pre-registered DL analysis (see reports/analysis_plan.md). Outputs reports/results_dl.json and prints a summary."""
import sys, json; sys.path.insert(0, "src")
import numpy as np, pandas as pd
from features import drill_features
rng = np.random.default_rng(2027); R = "/home/claude/data/raw/"
DL_DRILLS = ["PASS_RUSH_DRILL", "FRONT_START_WAVE_DRILL_AND_LATERAL_REACTION", "BODY_CONTROL_DRILL", "FOUR_BAG_AGILITY_DRILL", "RUN_THE_HOOP_DRILL", "RUN_AND_CLUB_DRILL"]
FEATS = ["peak_speed", "peak_accel", "peak_brake", "max_turn_rate"]
# ---- Combine attempt features
ct = pd.read_csv(R + "combine_tracking.csv"); ct = ct[(ct.entity_type == "PLAYER") & ct.drill_name.isin(DL_DRILLS)].copy()
ct["t"] = pd.to_datetime(ct.time); ct = ct.sort_values(["event_id", "t"])
rows = []
for ev, e in ct.groupby("event_id"):
    r = drill_features(e); r.update(event_id=ev, nfl_id=int(e.nfl_id.iloc[0]), drill=e.drill_name.iloc[0], attempt=int(e.attempt.iloc[0])); rows.append(r)
att = pd.DataFrame(rows)
# reliability: odd/even attempts per drill & feature (Spearman-Brown)
rel = {}
for d in DL_DRILLS:
    a = att[att.drill == d].sort_values("attempt"); a["k"] = a.groupby("nfl_id").cumcount()
    a = a[a.k < 2].pivot(index="nfl_id", columns="k", values=FEATS).dropna()
    if (a.shape[1] < 2 * len(FEATS)) or len(a) < 10:
        for f in FEATS: rel[f"{d}|{f}"] = dict(n=int(len(a)), r=None, sb=None, note="single attempt per player; test-retest not estimable")
        continue
    for f in FEATS:
        r = np.corrcoef(a[f][0], a[f][1])[0, 1]; rel[f"{d}|{f}"] = dict(n=len(a), r=float(r), sb=float(2 * r / (1 + r)))
json.dump(rel, open("reports/reliability_dl_drills.json", "w"), indent=1)
pm = att.groupby(["nfl_id", "drill"])[FEATS].mean().reset_index()
z = pm.copy()
for f in FEATS: z[f] = z.groupby("drill")[f].transform(lambda s: (s - s.mean()) / s.std())
comp = z.groupby("nfl_id")[FEATS].mean().add_prefix("trk_").reset_index()
comp["n_drills"] = z.groupby("nfl_id").drill.nunique().values
# ---- Outcome: adjusted player get-off (empirical Bayes)
pp = pd.read_csv(R + "player_play.csv", low_memory=False); g = pd.read_csv(R + "games.csv"); cr = pd.read_csv(R + "combine_results.csv"); pl = pd.read_csv(R + "players.csv")
pp = pp.merge(g[["game_id", "season", "season_type"]], on="game_id").merge(cr[["nfl_id", "combine_position"]], on="nfl_id")
s = pp[(pp.season_type == "REG") & (pp.play_nullified_by_penalty != "Y") & (pp.combine_position == "DL") & pp.player_get_off.notna()].copy()
s["dropback"] = s.pass_result.notna().astype(int); s["align"] = np.where(s.lined_up_position.isin(["EDGE", "INTERIOR_LINE"]), s.lined_up_position, "OTHER")
X = pd.get_dummies(s[["align", "dropback", "season"]].astype({"season": str}), drop_first=True).astype(float); X.insert(0, "c", 1.0)
beta = np.linalg.lstsq(X.values, s.player_get_off.values, rcond=None)[0]; s["resid"] = s.player_get_off.values - X.values @ beta
pg = s.groupby("nfl_id").resid.agg(["mean", "size", "var"]).reset_index(); pg = pg[pg["size"] >= 100]
sw2 = np.average(pg["var"], weights=pg["size"] - 1); tau2 = max(pg["mean"].var() - np.mean(sw2 / pg["size"]), 1e-6)
pg["eb"] = -(pg["mean"] * tau2 / (tau2 + sw2 / pg["size"]))      # negated: higher = faster get-off
reliab = tau2 / (tau2 + np.mean(sw2 / pg["size"]))
# ---- Assemble
D = pg.merge(cr, on="nfl_id").merge(pl[["nfl_id", "draft_overall_pick", "nfl_position"]], on="nfl_id").merge(comp, on="nfl_id", how="left")
D["pick"] = D.draft_overall_pick.fillna(260.0); D["log_pick"] = np.log(D.pick)
base = ["forty", "ten_yd_split", "three_cone", "short_shuttle", "vertical", "broad_jump", "combine_height", "combine_weight", "arm_length", "wing_span", "log_pick"]
trk = ["trk_" + f for f in FEATS]
def prep(tr, te, cols):
    A, B = tr[cols].copy(), te[cols].copy(); med = A.median()
    for c in cols:
        if A[c].isna().any() or B[c].isna().any():
            A[c + "_na"], B[c + "_na"] = A[c].isna().astype(float), B[c].isna().astype(float)
    A, B = A.fillna(med), B.fillna(med); mu, sd = A.mean(), A.std().replace(0, 1); A, B = (A - mu) / sd, (B - mu) / sd
    return A.fillna(0).values, B.reindex(columns=A.columns if False else B.columns).fillna(0).values
def ridge_pred(tr, te, cols, lam):
    A, B = prep(tr, te, cols); y = tr.eb.values; ym = y.mean()
    w = np.linalg.solve(A.T @ A + lam * np.eye(A.shape[1]), A.T @ (y - ym)); return B @ w + ym
def r2(y, p, ybar): return 1 - ((y - p) ** 2).sum() / ((y - ybar) ** 2).sum()
D = D.dropna(subset=["eb"]).reset_index(drop=True); has = D[trk].notna().all(axis=1) & (D.n_drills >= 4); D = D[has].reset_index(drop=True)
out = dict(n_players=len(D), outcome_reliability=float(reliab), snaps=int(D["size"].sum()))
def cv(cols_sets, lam, scheme):
    preds = {k: np.zeros(len(D)) for k in cols_sets}; 
    folds = [(D.index[D.draft_year != c], D.index[D.draft_year == c]) for c in sorted(D.draft_year.unique())] if scheme == "loco" else None
    if scheme != "loco":
        idx = rng.permutation(len(D)); parts = np.array_split(idx, 5); folds = [(np.setdiff1d(idx, p), p) for p in parts]
    for tr, te in folds:
        for k, cols in cols_sets.items(): preds[k][te] = ridge_pred(D.loc[tr], D.loc[te], cols, lam)
    return preds
sets = {"baseline": base, "tracking_only": trk, "baseline+tracking": base + trk, "forty_only": ["forty"], "weight_only": ["combine_weight"], "pick_only": ["log_pick"]}
y = D.eb.values; res = {}
for scheme in ["loco", "cv5x20"]:
    for lam in [10.0, 30.0]:
        reps = 1 if scheme == "loco" else 20; accum = {k: [] for k in sets}
        for _ in range(reps):
            p = cv(sets, lam, "loco" if scheme == "loco" else "cv"); 
            for k in sets: accum[k].append(p[k])
        res[f"{scheme}|lam={lam}"] = {k: float(np.mean([r2(y, p, y.mean()) for p in accum[k]])) for k in sets}
        if scheme == "loco" and lam == 10.0: P = {k: accum[k][0] for k in sets}
out["oos_r2"] = res
# bootstrap players for delta R2 (baseline+tracking minus baseline), LOCO predictions fixed (approximation)
B = 2000; dl = []
for _ in range(B):
    i = rng.integers(0, len(D), len(D)); dl.append(r2(y[i], P["baseline+tracking"][i], y[i].mean()) - r2(y[i], P["baseline"][i], y[i].mean()))
out["delta_r2_loco_lam10"] = dict(est=float(r2(y, P["baseline+tracking"], y.mean()) - r2(y, P["baseline"], y.mean())), ci95=[float(np.percentile(dl, 2.5)), float(np.percentile(dl, 97.5))])
# descriptive associations (Spearman) with FDR across the 4 composites + conventional measures
from scipy.stats import spearmanr
asc = {c: dict(zip(["rho", "p"], map(float, spearmanr(D[c], y, nan_policy="omit")))) for c in base + trk}
ps = np.array([v["p"] for v in asc.values()]); o = np.argsort(ps); m = len(ps); q = np.empty(m); q[o] = np.minimum.accumulate((ps[o] * m / (np.arange(m) + 1))[::-1])[::-1]
for k, qq in zip(asc, q): asc[k]["q_bh"] = float(min(qq, 1))
out["spearman"] = asc
# partial: tracking composites controlling alignment mix + weight
out["class_counts"] = D.draft_year.value_counts().to_dict(); out["position_counts"] = D.nfl_position.value_counts().to_dict()
json.dump(out, open("reports/results_dl.json", "w"), indent=1, default=float); D.to_csv("/home/claude/data/dl_player_table.csv", index=False)
print(json.dumps({k: out[k] for k in ["n_players", "snaps", "outcome_reliability", "class_counts", "position_counts"]}, default=float))
for k, v in res.items(): print(k, {a: round(b, 3) for a, b in v.items()})
print("delta R2:", out["delta_r2_loco_lam10"])
for k, v in asc.items(): print(f"{k:16s} rho={v['rho']:+.2f} p={v['p']:.3f} q={v['q_bh']:.3f}")
