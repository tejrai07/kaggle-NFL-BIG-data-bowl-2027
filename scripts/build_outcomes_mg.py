"""Outcome construction for WR (separation) and OL (pressure allowed) per reports/multigroup_analysis_plan.md. No Combine data is used here."""
import sys, json, os; sys.path.insert(0, "src")
import pandas as pd, numpy as np, multigroup as m
R = "/home/claude/data/raw/"; O = "/home/claude/data/mg/"; os.makedirs(O, exist_ok=True)
pp = pd.read_csv(R + "player_play.csv", low_memory=False); g = pd.read_csv(R + "games.csv"); cr = pd.read_csv(R + "combine_results.csv"); pl = pd.read_csv(R + "players.csv")
n_all = len(pp)
pp = pp.merge(g[["game_id", "season", "season_type", "week"]], on="game_id", validate="m:1").merge(cr[["nfl_id", "combine_position", "draft_year"]], on="nfl_id", validate="m:1")
assert len(pp) == n_all, "join changed row count"
reg = pp[(pp.season_type == "REG") & (pp.play_nullified_by_penalty != "Y")].copy(); info = {}
def collapse(s, keep): return np.where(s.isin(keep), s, "OTHER")
# ---------------- WR
w = reg[(reg.combine_position == "WR") & reg.route_ran.notna() & reg.separation_at_pass_forward.notna()].copy()
w["align"] = collapse(w.lined_up_position, ["WR", "SLOT_WR", "TE"]); w["cov"] = w.team_coverage_man_zone.fillna("UNK")
X = m.design(w, ["route_ran", "align", "cov", "season"], ["cushion"]); b = np.linalg.lstsq(X.values, w.separation_at_pass_forward.values, rcond=None)[0]
w["resid"] = w.separation_at_pass_forward.values - X.values @ b
info["WR"] = dict(snaps=len(w), players=int(w.nfl_id.nunique()), sep_mean=float(w.separation_at_pass_forward.mean()), sep_sd=float(w.separation_at_pass_forward.std()),
                  resid_sd=float(w.resid.std()), r2_snap_model=float(1 - w.resid.var() / w.separation_at_pass_forward.var()), cushion_missing=float(w.cushion.isna().mean()),
                  align=w["align"].value_counts().to_dict())
# ---------------- OL
o = reg[(reg.combine_position == "OL") & reg.pass_result.notna() & reg.pressure_allowed.notna()].copy()
o["y"] = o.pressure_allowed.astype(float); o["align"] = collapse(o.lined_up_position, ["T", "G", "C"]); o["cov"] = o.team_coverage_man_zone.fillna("UNK")
o["down_c"] = o.down.astype("Int64").astype(str); o["ytg"] = o.yards_to_go.clip(upper=20); o["form"] = o.offense_formation.fillna("UNK")
Xo = m.design(o, ["align", "down_c", "form", "cov", "season"], ["ytg"]); bo = m.logistic_irls(Xo.values, o.y.values)
o["phat"] = 1 / (1 + np.exp(-(Xo.values @ bo))); o["resid"] = o.y - o.phat
info["OL"] = dict(snaps=len(o), players=int(o.nfl_id.nunique()), pressure_rate=float(o.y.mean()), phat_sd=float(o.phat.std()), align=o["align"].value_counts().to_dict(),
                  rushers_encountered_zero_share=float((o.pass_rushers_encountered == 0).mean()))
o["resid"] = -o.resid     # higher = fewer pressures allowed than expected
w.to_csv(O + "snaps_WR.csv", index=False, columns=["game_id", "play_id", "nfl_id", "season", "draft_year", "resid", "separation_at_pass_forward"])
o.to_csv(O + "snaps_OL.csv", index=False, columns=["game_id", "play_id", "nfl_id", "season", "draft_year", "resid", "y"])
for grp, sn in (("WR", w), ("OL", o)):
    for tag, (mn, rk) in {"min100": (100, False), "min50": (50, False), "min200": (200, False), "rookie50": (50, True)}.items():
        s = sn[sn.season == sn.draft_year] if rk else sn
        pg = m.eb_shrink(s, min_n=mn); sh, nsh = m.split_half_reliability(s, min_n=mn)
        rel = float(pg.attrs["reliability"]); pg = pg.merge(cr[["nfl_id", "draft_year"]], on="nfl_id"); pg.to_csv(O + f"players_{grp}_{tag}.csv", index=False)
        info[grp][tag] = dict(players=int(len(pg)), snaps=int(pg["size"].sum()), eb_reliability_formula=rel, split_half_game_parity_sb=sh, n_split=nsh,
                              by_class=pg.draft_year.value_counts().sort_index().to_dict())
json.dump(info, open("reports/outcome_construction_mg.json", "w"), indent=1, default=float)
print(json.dumps(info, indent=1, default=float))
