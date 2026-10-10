"""Confirmatory + sensitivity analysis per reports/multigroup_analysis_plan.md. Verifies plan hash before running."""
import sys, json, hashlib, os; sys.path.insert(0, "src")
import numpy as np, pandas as pd
from scipy.stats import spearmanr, rankdata
import multigroup as m
PLAN = "reports/multigroup_analysis_plan.md"; want = open("reports/plan_hashes.txt").read().split()[0]
assert hashlib.sha256(open(PLAN, "rb").read()).hexdigest() == want, "PLAN FILE CHANGED AFTER PRE-SPECIFICATION"; print("plan hash verified")
R = "/home/claude/data/raw/"; O = "/home/claude/data/mg/"
cr = pd.read_csv(R + "combine_results.csv").drop(columns=["draft_year"]); pl = pd.read_csv(R + "players.csv")[["nfl_id", "draft_overall_pick"]]
conv = cr.merge(pl, on="nfl_id"); conv["log_pick"] = np.log(conv.draft_overall_pick.fillna(260.0))
def assemble(g, tag="min100", how="mean"):
    pg = pd.read_csv(O + f"players_{g}_{tag}.csv"); c = pd.read_csv(O + f"composites_{g}_{how}.csv")
    D = pg.merge(c, on="nfl_id", how="left"); n_out = len(D); D = D.dropna(subset=m.TRK).merge(conv, on="nfl_id", validate="1:1").reset_index(drop=True)
    D.attrs.update(n_outcome_eligible=n_out); return D
def classify(r, p_adj):
    if p_adj < 0.05 and r["ci_lo"] > 0: return "ADDS_INFORMATION"
    return "INCONCLUSIVE" if r["ci_hi"] >= 0.10 else "NO_DETECTABLE_GAIN"
out = {"plan_sha256": want}; fam = {}
# ---- DL frozen design (fixed lambda=10, saved frozen player table)
DL = pd.read_csv("/home/claude/data/dl_player_table.csv"); 
r, P = m.evaluate(DL, m.BASE_FULL, lam=10.0); fam["DL"] = r; out["DL_frozen_design"] = r
r2, _ = m.evaluate(DL, m.BASE_FULL, lam=None); out["DL_harmonized_nested_supplementary"] = r2
data = {"DL": DL}
for g in ["WR", "OL", "DB"]:
    D = assemble(g); data[g] = D; r, P = m.evaluate(D, m.BASE_FULL, lam=None); r["n_outcome_eligible"] = D.attrs["n_outcome_eligible"]; r["by_class"] = D.draft_year.value_counts().sort_index().to_dict()
    r["snaps"] = int(D["size"].sum()); fam[g] = r; out[g] = {"primary": r}
out["DL_primary_context"] = dict(n=len(DL), snaps=int(DL["size"].sum()), by_class=DL.draft_year.value_counts().sort_index().to_dict())
order = ["DL", "WR", "OL", "DB"]; padj = m.bh_adjust([fam[k]["p_perm"] for k in order])
for k, pa in zip(order, padj): fam[k]["p_adj_bh"] = float(pa); fam[k]["classification"] = classify(fam[k], pa)
# ---- descriptive / flags
def partial(x, y, Z):
    Zr = np.column_stack([np.ones(len(x))] + [rankdata(z) for z in Z.T]); rx, ry = rankdata(x), rankdata(y)
    return np.corrcoef(rx - Zr @ np.linalg.lstsq(Zr, rx, rcond=None)[0], ry - Zr @ np.linalg.lstsq(Zr, ry, rcond=None)[0])[0, 1]
for g in order:
    D = data[g]; y = D.eb.values; desc = {}
    for c in m.BASE_FULL + m.TRK:
        v = D[c]; ok = v.notna()
        rho, p = spearmanr(v[ok], y[ok]); desc[c] = dict(rho=float(rho), p=float(p), n=int(ok.sum()))
    qs = m.bh_adjust([desc[c]["p"] for c in desc])
    for c, q in zip(desc, qs): desc[c]["q_bh_within_group"] = float(q)
    E = D[["forty", "combine_weight", "vertical"]].fillna(D[["forty", "combine_weight", "vertical"]].median()); Xc = np.column_stack([np.ones(len(D)), E.values]); red = {}; part = {}
    for c in m.TRK:
        yy = D[c].values; red[c] = float(1 - ((yy - Xc @ np.linalg.lstsq(Xc, yy, rcond=None)[0]) ** 2).sum() / ((yy - yy.mean()) ** 2).sum())
        part[c] = float(partial(D[c].values, y, D[["forty", "combine_weight"]].fillna(D[["forty", "combine_weight"]].median()).values))
    flags = dict(redundancy_median_R2=float(np.median(list(red.values()))), redundancy_flag=bool(np.median(list(red.values())) >= 0.50), redundancy_R2=red, partial_rho_given_forty_weight=part)
    out.setdefault(g, {}); out[g].update(descriptive_exploratory=desc, flags=flags)
# reliability flags
import multigroup as mm
ct = pd.read_csv(R + "combine_tracking.csv"); crr = pd.read_csv(R + "combine_results.csv")
DLD = ["PASS_RUSH_DRILL", "FRONT_START_WAVE_DRILL_AND_LATERAL_REACTION", "BODY_CONTROL_DRILL", "FOUR_BAG_AGILITY_DRILL", "RUN_THE_HOOP_DRILL", "RUN_AND_CLUB_DRILL"]
att_dl = mm.attempt_table(ct, ["SKILL_DRILLS_DL"]); ids_dl = crr[crr.combine_position == "DL"].nfl_id.values
rel = {"DL": mm.drill_reliability(att_dl, ids_dl, DLD)}
for g in ["WR", "OL", "DB"]: rel[g] = pd.read_csv(O + f"reliability_{g}.csv")
summ = json.load(open("reports/combine_feature_summary_mg.json"))
for g in order:
    rr = rel[g]; vals = rr.sb.dropna(); nd = rr.drill.nunique(); single = int(sum(rr[rr.drill == d].sb.isna().all() for d in rr.drill.unique()))
    out[g]["flags"].update(reliability_median_sb=float(vals.median()) if len(vals) else None, reliability_flag=bool(len(vals) and vals.median() < 0.5), n_cells=int(len(vals)), n_drills=int(nd), single_attempt_drills=single,
                           reliability_by_feature={f: (float(rr[rr.feat == f].sb.median()) if rr[rr.feat == f].sb.notna().any() else None) for f in m.FEATS})
# ---- sensitivities (non-confirmatory; no perm test)
sens = {}
def run(D, **kw):
    r, _ = m.evaluate(D, perm=False, B_boot=2000, **kw); return {k: r[k] for k in ["n", "r2_base", "r2_enh", "r2_trk_only", "delta", "ci_lo", "ci_hi"]}
for g in ["WR", "OL", "DB"]:
    s = {}
    for tag in ["min50", "min200", "rookie50"]: s[tag] = run(assemble(g, tag), base_cols=m.BASE_FULL, lam=None)
    s["parsimonious_baseline"] = run(data[g], base_cols=m.BASE_PARSIMONIOUS, lam=None); s["best_attempt_composites"] = run(assemble(g, "min100", "best"), base_cols=m.BASE_FULL, lam=None); sens[g] = s
s = {"parsimonious_baseline_lam10": run(DL, base_cols=m.BASE_PARSIMONIOUS, lam=10.0), "parsimonious_baseline_nested": run(DL, base_cols=m.BASE_PARSIMONIOUS, lam=None)}
cd = mm.composites(att_dl, ids_dl, DLD, how="best"); Db = DL.drop(columns=m.TRK + ["n_drills"]).merge(cd, on="nfl_id").reset_index(drop=True); s["best_attempt_composites_lam10"] = run(Db, base_cols=m.BASE_FULL, lam=10.0)
s["not_run"] = "min-snap thresholds and rookie-only outcome not rebuilt for the frozen DL design"; sens["DL"] = s
out["family"] = fam; out["sensitivity"] = sens
json.dump(out, open("reports/results_multigroup.json", "w"), indent=1, default=float)
print(f"{'grp':4s} {'n':>3s} {'R2 base':>8s} {'R2 enh':>8s} {'R2 trk':>8s} {'delta':>7s} {'CI95':>17s} {'p_perm':>7s} {'p_BH':>6s}  class")
for k in order:
    r = fam[k]; print(f"{k:4s} {r['n']:3d} {r['r2_base']:8.3f} {r['r2_enh']:8.3f} {r['r2_trk_only']:8.3f} {r['delta']:+7.3f} [{r['ci_lo']:+.3f},{r['ci_hi']:+.3f}] {r['p_perm']:7.3f} {r['p_adj_bh']:6.3f}  {r['classification']}")
print("DL harmonized nested (supplementary):", {k: round(v, 3) if isinstance(v, float) else v for k, v in out["DL_harmonized_nested_supplementary"].items() if k in ["r2_base", "r2_enh", "r2_trk_only", "delta", "ci_lo", "ci_hi", "p_perm"]})
