"""Integration + fixture tests for joins and outcome construction. Real-data tests are skipped if the raw CSVs are absent."""
import sys, os, numpy as np, pandas as pd; sys.path.insert(0, "src")
import multigroup as m
R, O = "/home/claude/data/raw/", "/home/claude/data/mg/"; HAVE = os.path.exists(R + "player_play.csv") and os.path.exists(O + "snaps_WR.csv")
def skip(): print("  (skipped: data absent)")
def test_design_matrix_fixture():
    df = pd.DataFrame({"c": ["a", "b", "a", "c"], "x": [1.0, np.nan, 3.0, 4.0]}); X = m.design(df, ["c"], ["x"])
    assert list(X.columns) == ["const", "c_b", "c_c", "x", "x_na"] or set(X.columns) >= {"const", "x", "x_na"}; assert X.x.isna().sum() == 0 and X.x_na.sum() == 1
def test_eb_fixture_has_no_player_below_min_n():
    s = pd.DataFrame({"nfl_id": [1] * 120 + [2] * 40, "game_id": list(range(120)) + list(range(40)), "resid": np.random.default_rng(0).normal(size=160)})
    assert set(m.eb_shrink(s, min_n=100).nfl_id) == {1}
def test_join_cardinality_player_play_games_players():
    if not HAVE: return skip()
    pp = pd.read_csv(R + "player_play.csv", usecols=["game_id", "play_id", "nfl_id"]); g = pd.read_csv(R + "games.csv"); pl = pd.read_csv(R + "players.csv")
    assert not pp.duplicated().any() and g.game_id.is_unique and pl.nfl_id.is_unique
    assert len(pp.merge(g[["game_id"]], on="game_id", validate="m:1")) == len(pp) and len(pp.merge(pl[["nfl_id"]], on="nfl_id", validate="m:1")) == len(pp)
def test_outcome_snaps_are_regular_season_non_nullified_and_unique():
    if not HAVE: return skip()
    pp = pd.read_csv(R + "player_play.csv", usecols=["game_id", "play_id", "nfl_id", "play_nullified_by_penalty", "pass_result", "route_ran", "separation_at_pass_forward", "pressure_allowed"])
    g = pd.read_csv(R + "games.csv")[["game_id", "season_type"]]; cr = pd.read_csv(R + "combine_results.csv")[["nfl_id", "combine_position"]]
    for grp, f in [("WR", "snaps_WR.csv"), ("OL", "snaps_OL.csv"), ("DB", "snaps_DB.csv")]:
        s = pd.read_csv(O + f, usecols=["game_id", "play_id", "nfl_id"]); assert not s.duplicated().any(), grp + " duplicate snaps"
        j = s.merge(pp, on=["game_id", "play_id", "nfl_id"], validate="1:1").merge(g, on="game_id").merge(cr, on="nfl_id")
        assert (j.season_type == "REG").all() and (j.play_nullified_by_penalty != "Y").all() and (j.combine_position == grp).all(), grp
        if grp == "WR": assert j.route_ran.notna().all() and j.separation_at_pass_forward.notna().all()
        if grp == "OL": assert j.pass_result.notna().all() and j.pressure_allowed.notna().all()
        if grp == "DB": assert j.pass_result.notna().all()
def test_player_tables_unique_min_snaps_and_class_match():
    if not HAVE: return skip()
    cr = pd.read_csv(R + "combine_results.csv")[["nfl_id", "draft_year"]]
    for g in ["WR", "OL", "DB"]:
        for tag, mn in [("min100", 100), ("min50", 50), ("min200", 200)]:
            p = pd.read_csv(O + f"players_{g}_{tag}.csv" if g != "WR" and g != "OL" else O + f"players_{g}_{tag}.csv"); assert p.nfl_id.is_unique and (p["size"] >= mn).all()
            assert (p.merge(cr, on="nfl_id", suffixes=("", "_c")).eval("draft_year == draft_year_c")).all()
def test_wr_residuals_centered_and_ol_residual_sign():
    if not HAVE: return skip()
    w = pd.read_csv(O + "snaps_WR.csv"); assert abs(w.resid.mean()) < 1e-8                              # OLS with intercept -> mean zero
    o = pd.read_csv(O + "snaps_OL.csv"); assert abs(o.resid.mean()) < 0.01 and np.corrcoef(o.resid, o.y)[0, 1] < -0.9   # flipped: pressure allowed -> lower (worse)
def test_db_window_rules():
    if not HAVE: return skip()
    d = pd.read_csv(O + "snaps_DB.csv"); assert d.window_s.between(2.0, 3.0).all() and d.lined_up_position.isin(["CB", "SLOT_CB", "HIGH_SAFETY"]).all()
def test_composites_players_have_enough_drills():
    if not HAVE: return skip()
    import json; s = json.load(open("reports/combine_feature_summary_mg.json"))
    for g in ["WR", "OL", "DB"]:
        c = pd.read_csv(O + f"composites_{g}_mean.csv"); assert c.nfl_id.is_unique and (c.n_drills >= int(np.ceil(2 / 3 * s[g]["n_eligible"]))).all()
