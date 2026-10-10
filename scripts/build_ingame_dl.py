"""Extract first-1.5s-after-snap movement for DL (Combine position group) regular-season, non-nullified snaps with player_get_off.
Chunked; keeps only needed plays. Output: data/ingame_dl_snaps.csv (one row per player-play)."""
import pandas as pd, numpy as np, sys
R = "/home/claude/data/raw/"; OUT = "/home/claude/data/ingame_dl_snaps.csv"
pp = pd.read_csv(R + "player_play.csv", low_memory=False)
g = pd.read_csv(R + "games.csv"); cr = pd.read_csv(R + "combine_results.csv")
pp = pp.merge(g[["game_id", "season", "season_type", "week"]], on="game_id").merge(cr[["nfl_id", "combine_position", "draft_year"]], on="nfl_id")
sel = pp[(pp.season_type == "REG") & (pp.play_nullified_by_penalty != "Y") & (pp.combine_position == "DL") & pp.player_get_off.notna()]
keys = sel[["game_id", "play_id", "nfl_id"]].drop_duplicates()
print("selected player-plays:", len(keys))
parts = []
for yr in (2023, 2024, 2025):
    for ch in pd.read_csv(R + f"game_tracking_{yr}.csv", chunksize=1_000_000):
        m = ch.merge(keys, on=["game_id", "play_id", "nfl_id"])
        if len(m): parts.append(m)
tr = pd.concat(parts, ignore_index=True); tr["t"] = pd.to_datetime(tr.time)
tr = tr.sort_values(["game_id", "play_id", "nfl_id", "t"]).reset_index(drop=True)
print("frames kept:", len(tr))
dirmap = sel.set_index(["game_id", "play_id", "nfl_id"]).play_direction
rows = []
for (gid, pid, nid), e in tr.groupby(["game_id", "play_id", "nfl_id"], sort=False):
    ev = e.event.values; idx = np.flatnonzero(ev == "ball_snap")
    if len(idx) != 1: rows.append(dict(game_id=gid, play_id=pid, nfl_id=nid, ok=False, why="snap_events=%d" % len(idx))); continue
    s0 = idx[0]; w = e.iloc[s0:s0 + 16]
    if len(w) < 16: rows.append(dict(game_id=gid, play_id=pid, nfl_id=nid, ok=False, why="short")); continue
    sign = -1.0 if dirmap.loc[(gid, pid, nid)] == "right" else 1.0   # rushers move against offense's direction of travel
    x, y = w.x.values, w.y.values; step = np.hypot(np.diff(x), np.diff(y))
    rows.append(dict(game_id=gid, play_id=pid, nfl_id=nid, ok=True, why="",
        adv_1s=sign * (x[10] - x[0]), adv_15s=sign * (x[15] - x[0]), lat_1s=abs(y[10] - y[0]),
        path_1s=step[:10].sum(), spd_05=w.s.values[5], spd_10=w.s.values[10], spd_max_15=w.s.values[:16].max(),
        pre_spd=e.s.values[max(s0 - 1, 0)], pre_adv=0.0))
res = pd.DataFrame(rows); res.to_csv(OUT, index=False)
print(res.ok.value_counts().to_dict(), res[~res.ok].why.value_counts().to_dict())
