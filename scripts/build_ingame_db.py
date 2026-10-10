"""DB PHYSICAL-TRANSFER outcome (not coverage production): max in-game speed during pass coverage, window = snap -> min(pass_forward, snap+3.0s), >= 2.0 s.
Per reports/multigroup_analysis_plan.md section 2 (DB). No Combine data used."""
import sys, json, os; sys.path.insert(0, "src")
import pandas as pd, numpy as np, multigroup as m
R = "/home/claude/data/raw/"; O = "/home/claude/data/mg/"
pp = pd.read_csv(R + "player_play.csv", low_memory=False); g = pd.read_csv(R + "games.csv"); cr = pd.read_csv(R + "combine_results.csv")
n0 = len(pp); pp = pp.merge(g[["game_id", "season", "season_type"]], on="game_id", validate="m:1").merge(cr[["nfl_id", "combine_position", "draft_year"]], on="nfl_id", validate="m:1"); assert len(pp) == n0
sel = pp[(pp.season_type == "REG") & (pp.play_nullified_by_penalty != "Y") & (pp.combine_position == "DB") & pp.pass_result.notna()
         & pp.lined_up_position.isin(["CB", "SLOT_CB", "HIGH_SAFETY"]) & pp.coverage_assignment_at_snap.notna()].copy()
keys = sel[["game_id", "play_id", "nfl_id"]].drop_duplicates(); print("selected DB coverage snaps:", len(keys))
parts = []
for yr in (2023, 2024, 2025):
    for ch in pd.read_csv(f"{R}game_tracking_{yr}.csv", chunksize=1_000_000, usecols=["game_id", "play_id", "nfl_id", "time", "s", "event"]):
        mm = ch.merge(keys, on=["game_id", "play_id", "nfl_id"])
        if len(mm): parts.append(mm)
tr = pd.concat(parts, ignore_index=True); tr["t"] = pd.to_datetime(tr.time); tr = tr.drop(columns="time").sort_values(["game_id", "play_id", "nfl_id", "t"]).reset_index(drop=True)
print("frames kept:", len(tr)); rows = []; why = {}
for (gid, pid, nid), e in tr.groupby(["game_id", "play_id", "nfl_id"], sort=False):
    ev = e.event.values; sn = np.flatnonzero(ev == "ball_snap")
    if len(sn) != 1: why["snap_events!=1"] = why.get("snap_events!=1", 0) + 1; continue
    s0 = sn[0]; pf = np.flatnonzero(ev[s0:] == "pass_forward"); end = s0 + (pf[0] if len(pf) else 30); end = min(end, s0 + 30)
    if len(pf) == 0: why["no_pass_forward"] = why.get("no_pass_forward", 0) + 1; continue          # sack/scramble/no throw: window undefined
    if end - s0 < 20 or end >= len(e): why["window<2s_or_truncated"] = why.get("window<2s_or_truncated", 0) + 1; continue
    w = e.s.values[s0:end + 1]; rows.append(dict(game_id=gid, play_id=pid, nfl_id=nid, max_speed=float(w.max()), window_s=(end - s0) / 10))
res = pd.DataFrame(rows).merge(sel[["game_id", "play_id", "nfl_id", "lined_up_position", "coverage_assignment_at_snap", "team_coverage_man_zone", "season", "draft_year"]], on=["game_id", "play_id", "nfl_id"], validate="1:1")
print("usable snaps:", len(res), "excluded:", why)
res["man"] = np.where(res.coverage_assignment_at_snap == "MAN", "MAN", "NONMAN")
X = m.design(res, ["lined_up_position", "man", "season"], ["window_s"]); b = np.linalg.lstsq(X.values, res.max_speed.values, rcond=None)[0]; res["resid"] = res.max_speed.values - X.values @ b
res.to_csv(O + "snaps_DB.csv", index=False)
info = dict(selected=int(len(keys)), usable=int(len(res)), excluded=why, players=int(res.nfl_id.nunique()), max_speed_mean=float(res.max_speed.mean()), max_speed_sd=float(res.max_speed.std()),
            resid_sd=float(res.resid.std()), r2_snap_model=float(1 - res.resid.var() / res.max_speed.var()), lined_up=res.lined_up_position.value_counts().to_dict(), man_share=float((res.man == "MAN").mean()))
for tag, (mn, rk) in {"min100": (100, False), "min50": (50, False), "min200": (200, False), "rookie50": (50, True)}.items():
    s = res[res.season == res.draft_year] if rk else res
    pg = m.eb_shrink(s, min_n=mn); rel = float(pg.attrs["reliability"]); sh, nsh = m.split_half_reliability(s, min_n=mn); pg = pg.merge(cr[["nfl_id", "draft_year"]], on="nfl_id"); pg.to_csv(O + f"players_DB_{tag}.csv", index=False)
    info[tag] = dict(players=int(len(pg)), snaps=int(pg["size"].sum()), eb_reliability_formula=rel, split_half_game_parity_sb=sh, by_class=pg.draft_year.value_counts().sort_index().to_dict())
d = json.load(open("reports/outcome_construction_mg.json")); d["DB_physical"] = info; json.dump(d, open("reports/outcome_construction_mg.json", "w"), indent=1, default=float)
print(json.dumps(info, indent=1, default=float))
