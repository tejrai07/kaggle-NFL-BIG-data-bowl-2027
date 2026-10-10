import sys, numpy as np, pandas as pd; sys.path.insert(0, "src")
import multigroup as m
def test_harmonize_and_eligibility():
    assert m.harmonize("LINE") == "LINE_DRILL" and m.harmonize("PASS_PRO-MIRROR_DRILL") == "PASS_PRO_MIRROR_DRILL" and m.harmonize("GO_ROUTE_RIGHT") == "GO_ROUTE_RIGHT"
    att = pd.DataFrame({"nfl_id": [1, 2, 3, 1, 2], "drill": ["A", "A", "A", "B", "B"]}); assert m.eligible_drills(att, [1, 2, 3], 0.8) == ["A"]
def test_composite_requires_drill_fraction_and_zscores():
    rows = [dict(nfl_id=i, drill=d, **{f: float(i + j) for f in m.FEATS}) for i in range(1, 7) for j, d in enumerate(["A", "B", "C"]) if not (i == 6 and d != "A")]
    c = m.composites(pd.DataFrame(rows), list(range(1, 7)), ["A", "B", "C"]); assert 6 not in set(c.nfl_id) and abs(c.trk_peak_speed.mean()) < 0.5
def test_logistic_irls_recovers_coefficients():
    rng = np.random.default_rng(0); X = np.column_stack([np.ones(20000), rng.normal(size=20000)]); y = (rng.random(20000) < 1 / (1 + np.exp(-(X @ [-1.0, 0.8])))).astype(float)
    assert np.allclose(m.logistic_irls(X, y), [-1.0, 0.8], atol=0.06)
def test_eb_shrinks_toward_zero_and_orders_by_n():
    rng = np.random.default_rng(1); rows = []
    for pid, n, mu in [(1, 400, 1.0), (2, 100, 1.0), (3, 100, -1.0), (4, 400, -1.0), (5, 250, 0.0), (6, 250, 0.1)]:
        rows += [dict(nfl_id=pid, game_id=g, resid=mu + rng.normal(scale=3)) for g in range(n)]
    pg = m.eb_shrink(pd.DataFrame(rows)).set_index("nfl_id"); assert abs(pg.loc[2, "eb"]) < abs(pg.loc[2, "mean"]); assert 0 < pg.attrs["reliability"] < 1
def test_loco_no_leakage_and_detects_leak():
    ids = np.array([1, 2, 3, 4, 5, 6]); cl = np.array([2023, 2023, 2024, 2024, 2025, 2025]); assert m.split_check(cl, ids)
    try: m.split_check(cl, np.array([1, 2, 3, 4, 5, 1])); raise SystemExit("leak not detected")
    except AssertionError: pass
def test_prep_uses_train_statistics_only():
    tr = np.array([[1., 10.], [2., 20.], [3., np.nan]]); te = np.array([[100., 5.]]); A, B = m.prep(tr, te)
    assert np.allclose(A[:, 0].mean(), 0) and B[0, 0] > 50                       # test row standardized with TRAIN mean/sd
def test_ridge_recovers_signal_and_delta_zero_for_noise():
    rng = np.random.default_rng(3); n = 90; x = rng.normal(size=(n, 3)); cl = np.repeat([2023, 2024, 2025], 30); y = x[:, 0] * 1.0 + rng.normal(scale=0.5, size=n)
    p, _ = m.loco_predict(x, y, cl, lam=1.0); assert m.r2_oos(y, p) > 0.6
def test_bootstrap_ci_and_permutation_calibration():
    rng = np.random.default_rng(4); n = 60; xc = rng.normal(size=(n, 2)); xt = rng.normal(size=(n, 4)); cl = np.repeat([2023, 2024, 2025], 20)
    y = xc[:, 0] + rng.normal(size=n); pb, _ = m.loco_predict(xc, y, cl, lam=10.0); pe, _ = m.loco_predict(np.column_stack([xc, xt]), y, cl, lam=10.0)
    d = m.r2_oos(y, pe) - m.r2_oos(y, pb); lo, hi = m.bootstrap_delta(y, pb, pe, B=500); assert lo < hi
    assert m.permutation_p(xc, xt, y, cl, pb, d, lam=10.0, B=60) > 0.05                # pure-noise tracking should not look significant
def test_bh_adjust():
    assert np.allclose(m.bh_adjust([0.01, 0.04, 0.03, 0.5]), [0.04, 0.0533333, 0.0533333, 0.5], atol=1e-6)
def test_nested_lambda_selects_from_grid():
    rng = np.random.default_rng(5); X = rng.normal(size=(60, 5)); y = X[:, 0] + rng.normal(size=60); assert m.choose_lambda(X, y) in m.LAMBDAS
