"""Reusable statistics + feature code for the multi-group analysis (see reports/multigroup_analysis_plan.md)."""
import numpy as np, pandas as pd
from features import drill_features
FEATS = ["peak_speed", "peak_accel", "peak_brake", "max_turn_rate"]
HARMONIZE = {"LINE": "LINE_DRILL", "PASS_PRO-MIRROR_DRILL": "PASS_PRO_MIRROR_DRILL",
             "SPEED_OUT_LEFT": "SPEED_OUT_ROUTE_LEFT", "OVER_THE_SHOULDER_ADJUST": "OVER_SHOULDER_ADJUST"}
LAMBDAS = [1.0, 3.0, 10.0, 30.0, 100.0, 300.0]
BASE_FULL = ["forty", "ten_yd_split", "three_cone", "short_shuttle", "vertical", "broad_jump", "combine_height",
             "combine_weight", "arm_length", "wing_span", "log_pick"]
BASE_PARSIMONIOUS = ["forty", "combine_weight", "vertical", "log_pick"]
TRK = ["trk_" + f for f in FEATS]

# ---------------- Combine features
def harmonize(name): return HARMONIZE.get(name, name)
def attempt_table(ct, drill_types):
    f = ct[(ct.entity_type == "PLAYER") & ct.drill_type.isin(drill_types)].copy()
    f["t"] = pd.to_datetime(f.time); f = f.sort_values(["event_id", "t"]); rows = []
    for ev, e in f.groupby("event_id", sort=False):
        r = drill_features(e); r.update(event_id=ev, nfl_id=int(e.nfl_id.iloc[0]), drill_type=e.drill_type.iloc[0],
                                        drill=harmonize(e.drill_name.iloc[0]), attempt=int(e.attempt.iloc[0])); rows.append(r)
    return pd.DataFrame(rows)
def eligible_drills(att, group_ids, min_cov=0.80):
    a = att[att.nfl_id.isin(group_ids)]; cov = a.groupby("drill").nfl_id.nunique() / len(group_ids)
    return sorted(cov[cov >= min_cov].index)
def composites(att, group_ids, drills, min_frac=2 / 3, how="mean"):
    a = att[att.nfl_id.isin(group_ids) & att.drill.isin(drills)]
    agg = a.groupby(["nfl_id", "drill"])[FEATS].mean() if how == "mean" else \
        a.groupby(["nfl_id", "drill"])[FEATS].agg({"peak_speed": "max", "peak_accel": "max", "peak_brake": "min", "max_turn_rate": "max"})
    z = agg.reset_index()
    for f in FEATS: z[f] = z.groupby("drill")[f].transform(lambda s: (s - s.mean()) / s.std())
    out = z.groupby("nfl_id")[FEATS].mean().add_prefix("trk_"); out["n_drills"] = z.groupby("nfl_id").drill.nunique()
    return out[out.n_drills >= int(np.ceil(min_frac * len(drills)))].reset_index()
def drill_reliability(att, group_ids, drills):
    """Spearman-Brown test-retest per drill x feature for drills with >=2 attempts; single-attempt drills flagged."""
    res = []
    for d in drills:
        a = att[att.nfl_id.isin(group_ids) & (att.drill == d)].sort_values("attempt"); a["k"] = a.groupby("nfl_id").cumcount()
        w = a[a.k < 2].pivot(index="nfl_id", columns="k", values=FEATS).dropna() if (a.k >= 1).any() else pd.DataFrame()
        for f in FEATS:
            if len(w) >= 15 and w.shape[1] == 2 * len(FEATS):
                r = np.corrcoef(w[f][0], w[f][1])[0, 1]; res.append(dict(drill=d, feat=f, n=len(w), sb=2 * r / (1 + r)))
            else: res.append(dict(drill=d, feat=f, n=len(w), sb=np.nan))
    return pd.DataFrame(res)

# ---------------- Outcome helpers
def logistic_irls(X, y, iters=50, ridge=1e-6):
    b = np.zeros(X.shape[1])
    for _ in range(iters):
        p = 1 / (1 + np.exp(-np.clip(X @ b, -30, 30))); W = np.clip(p * (1 - p), 1e-6, None)
        step = np.linalg.solve(X.T @ (X * W[:, None]) + ridge * np.eye(X.shape[1]), X.T @ (y - p)); b += step
        if np.abs(step).max() < 1e-8: break
    return b
def design(df, cats, nums):
    X = pd.get_dummies(df[cats].astype(str), drop_first=True).astype(float) if cats else pd.DataFrame(index=df.index)
    for c in nums:
        v = df[c].astype(float); X[c] = v.fillna(v.median())
        if v.isna().any(): X[c + "_na"] = v.isna().astype(float)
    X.insert(0, "const", 1.0); return X
def eb_shrink(snaps, resid_col="resid", min_n=100, id_col="nfl_id"):
    """Empirical-Bayes player effects. Returns player table with mean, n, eb (same method as frozen DL code), plus tau2, sw2, reliability."""
    pg = snaps.groupby(id_col)[resid_col].agg(["mean", "size", "var"]).reset_index(); pg = pg[pg["size"] >= min_n].copy()
    sw2 = np.average(pg["var"], weights=pg["size"] - 1); tau2 = max(pg["mean"].var() - np.mean(sw2 / pg["size"]), 1e-6)
    pg["eb"] = pg["mean"] * tau2 / (tau2 + sw2 / pg["size"]); pg.attrs.update(tau2=tau2, sw2=sw2, reliability=tau2 / (tau2 + np.mean(sw2 / pg["size"])))
    return pg
def split_half_reliability(snaps, resid_col="resid", min_n=100, id_col="nfl_id"):
    """Odd/even GAME parity within player (respects within-game dependence); Spearman-Brown."""
    s = snaps.copy(); s["gr"] = s.groupby(id_col).game_id.rank(method="dense"); s["k"] = (s.gr % 2).astype(int)
    p = s.groupby([id_col, "k"])[resid_col].agg(["mean", "size"]).unstack(); n = s.groupby(id_col).size()
    p = p[(n >= min_n).reindex(p.index).fillna(False) & p["size"].notna().all(axis=1)]
    r = np.corrcoef(p["mean"][0], p["mean"][1])[0, 1]; return float(2 * r / (1 + r)), int(len(p))

# ---------------- Model evaluation
def prep(Xtr, Xte):
    """numpy replica of the frozen DL prep(): missing indicators (if NaN in train OR test), train-median imputation, train standardization."""
    Xtr, Xte = Xtr.astype(float), Xte.astype(float); ia, ib = [], []
    for c in range(Xtr.shape[1]):
        if np.isnan(Xtr[:, c]).any() or np.isnan(Xte[:, c]).any(): ia.append(np.isnan(Xtr[:, c]).astype(float)); ib.append(np.isnan(Xte[:, c]).astype(float))
    med = np.nanmedian(Xtr, axis=0); med = np.where(np.isnan(med), 0.0, med)
    A = np.where(np.isnan(Xtr), med, Xtr); B = np.where(np.isnan(Xte), med, Xte)
    if ia: A = np.column_stack([A] + ia); B = np.column_stack([B] + ib)
    mu = A.mean(0); sd = A.std(0, ddof=1); sd = np.where((sd == 0) | np.isnan(sd), 1.0, sd)
    return np.nan_to_num((A - mu) / sd), np.nan_to_num((B - mu) / sd)
def ridge_fit_predict(A, y, B, lam):
    ym = y.mean(); w = np.linalg.solve(A.T @ A + lam * np.eye(A.shape[1]), A.T @ (y - ym)); return B @ w + ym
def choose_lambda(Xtr, ytr, lambdas=LAMBDAS, k=5, seed=0):
    n = len(ytr); idx = np.random.default_rng(seed).permutation(n); folds = np.array_split(idx, k); err = np.zeros(len(lambdas))
    for f in folds:
        tr = np.setdiff1d(idx, f); A, B = prep(Xtr[tr], Xtr[f])
        for j, lam in enumerate(lambdas): err[j] += ((ytr[f] - ridge_fit_predict(A, ytr[tr], B, lam)) ** 2).sum()
    return lambdas[int(np.argmin(err))]
def loco_predict(X, y, classes, lam=None, seed=0):
    """Leave-one-class-out. lam=None -> nested inner-CV lambda per outer fold; else fixed. Returns pooled predictions and chosen lambdas."""
    pred = np.zeros(len(y)); chosen = {}
    for c in np.unique(classes):
        te, tr = classes == c, classes != c
        l = choose_lambda(X[tr], y[tr], seed=seed + int(c)) if lam is None else lam; chosen[int(c)] = l
        A, B = prep(X[tr], X[te]); pred[te] = ridge_fit_predict(A, y[tr], B, l)
    return pred, chosen
def r2_oos(y, p, ref=None):
    ref = y.mean() if ref is None else ref; return 1 - ((y - p) ** 2).sum() / ((y - ref) ** 2).sum()
def split_check(classes, ids):
    """Assert LOCO design has no player in both train and test, and every class is held out once."""
    for c in np.unique(classes):
        assert not (set(ids[classes == c]) & set(ids[classes != c])), "player leakage across classes"
    return True
def bootstrap_delta(y, p_base, p_enh, B=5000, seed=1):
    rng = np.random.default_rng(seed); n = len(y); d = np.empty(B)
    for b in range(B):
        i = rng.integers(0, n, n); d[b] = r2_oos(y[i], p_enh[i]) - r2_oos(y[i], p_base[i])
    return np.percentile(d, [2.5, 97.5])
def permutation_p(Xconv, Xtrk, y, classes, p_base, delta_obs, lam=None, B=1000, seed=2):
    rng = np.random.default_rng(seed); ge = 0
    for _ in range(B):
        Xp = np.column_stack([Xconv, Xtrk[rng.permutation(len(y))]]); pe, _ = loco_predict(Xp, y, classes, lam=lam)
        ge += (r2_oos(y, pe) - r2_oos(y, p_base)) >= delta_obs
    return (1 + ge) / (1 + B)
def bh_adjust(p):
    p = np.asarray(p, float); m = len(p); o = np.argsort(p); adj = np.empty(m)
    adj[o] = np.minimum.accumulate((p[o] * m / (np.arange(m) + 1))[::-1])[::-1]; return np.minimum(adj, 1.0)
def evaluate(D, base_cols, trk_cols=TRK, lam=None, B_boot=5000, B_perm=1000, perm=True, seed=0):
    y = D.eb.values.astype(float); cl = D.draft_year.values; ids = D.nfl_id.values; split_check(cl, ids)
    Xc = D[base_cols].values.astype(float); Xt = D[trk_cols].values.astype(float)
    pb, lb = loco_predict(Xc, y, cl, lam=lam, seed=seed); pe, le = loco_predict(np.column_stack([Xc, Xt]), y, cl, lam=lam, seed=seed)
    po, _ = loco_predict(Xt, y, cl, lam=lam, seed=seed)
    d = r2_oos(y, pe) - r2_oos(y, pb); ci = bootstrap_delta(y, pb, pe, B=B_boot, seed=seed + 1)
    out = dict(n=len(y), r2_base=r2_oos(y, pb), r2_enh=r2_oos(y, pe), r2_trk_only=r2_oos(y, po), delta=d, ci_lo=float(ci[0]), ci_hi=float(ci[1]),
               lambdas_base=lb, lambdas_enh=le)
    out["p_perm"] = permutation_p(Xc, Xt, y, cl, pb, d, lam=lam, B=B_perm, seed=seed + 2) if perm else None
    return out, (pb, pe, po)
