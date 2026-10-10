"""Combine tracking composites for WR/OL/DB (per plan sections 1-2). Outputs under /home/claude/data/mg/."""
import sys, json, os; sys.path.insert(0, "src")
import pandas as pd, numpy as np, multigroup as m
R = "/home/claude/data/raw/"; O = "/home/claude/data/mg/"; os.makedirs(O, exist_ok=True)
ct = pd.read_csv(R + "combine_tracking.csv"); cr = pd.read_csv(R + "combine_results.csv")
G = {"WR": "SKILL_DRILLS_WR", "OL": "SKILL_DRILLS_OL", "DB": "SKILL_DRILLS_DB"}; summ = {}
for g, dt in G.items():
    att = m.attempt_table(ct, [dt]); ids = cr[cr.combine_position == g].nfl_id.values
    dr = m.eligible_drills(att, ids); att.to_csv(O + f"attempts_{g}.csv", index=False)
    for how in ("mean", "best"):
        c = m.composites(att, ids, dr, how=how); c.to_csv(O + f"composites_{g}_{how}.csv", index=False)
    rel = m.drill_reliability(att, ids, dr); rel.to_csv(O + f"reliability_{g}.csv", index=False)
    summ[g] = dict(combine_players=int(len(ids)), eligible_drills=dr, n_eligible=len(dr), players_with_composites=int(len(c)),
                   attempts=int(len(att)), single_attempt_drills=[d for d in dr if rel[rel.drill == d].sb.isna().all()],
                   median_sb=float(rel.sb.median()) if rel.sb.notna().any() else None, n_sb_cells=int(rel.sb.notna().sum()))
    print(g, json.dumps(summ[g], default=float))
json.dump(summ, open("reports/combine_feature_summary_mg.json", "w"), indent=1)
