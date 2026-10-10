import json, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
r = json.load(open("reports/results_multigroup.json")); oc = json.load(open("reports/outcome_construction_mg.json"))
C = dict(blue="#0072B2", orange="#E69F00", grey="#666666", verm="#D55E00")
order = ["DL", "WR", "OL", "DB"]; names = {"DL": "DL (get-off)\nfrozen design", "WR": "WR (separation)", "OL": "OL (pressure allowed)", "DB": "DB (in-game top speed,\nphysical transfer only)"}
fam = r["family"]
# ---- Fig 1: incremental out-of-sample R2 of tracking beyond conventional
fig, ax = plt.subplots(figsize=(7.6, 3.9)); y = np.arange(len(order))[::-1]
for yi, g in zip(y, order):
    f = fam[g]; ax.errorbar(f["delta"], yi, xerr=[[f["delta"] - f["ci_lo"]], [f["ci_hi"] - f["delta"]]], fmt="o", color=C["blue"], capsize=4, ms=7, lw=2)
    ax.text(0.205, yi, f"n={f['n']}  p(BH)={f['p_adj_bh']:.2f}\nbaseline R\u00b2={f['r2_base']:.2f}", va="center", fontsize=8, color=C["grey"])
ax.axvline(0, color="k", lw=1); ax.axvline(0.10, color=C["verm"], lw=1.2, ls="--"); ax.text(0.108, -0.45, "practical-gain\nthreshold (+0.10)", color=C["verm"], fontsize=7.5, ha="left", va="bottom")
ax.set_yticks(y); ax.set_yticklabels([names[g] for g in order], fontsize=9); ax.set_xlim(-0.25, 0.36); ax.set_ylim(-0.6, len(order) - 0.1)
ax.set_xlabel("\u0394 out-of-sample R\u00b2 from adding 4 Combine-tracking composites\n(leave-one-draft-class-out; point = estimate, bar = 95% player-bootstrap CI)", fontsize=9)
ax.set_title("Tracking composites added no detectable out-of-sample\ninformation in any position group", fontsize=10.5, loc="left"); ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig("reports/figures/fig1_incremental_value.png", dpi=200); plt.close(fig)
# ---- Fig 2: diagnostics heatmap
rel_out = {"DL": r["DL_frozen_design"].get("n") and 0.94, "WR": oc["WR"]["min100"]["split_half_game_parity_sb"], "OL": oc["OL"]["min100"]["split_half_game_parity_sb"], "DB": oc["DB_physical"]["min100"]["split_half_game_parity_sb"]}
cols = ["Conventional\nbaseline\nout-of-sample R\u00b2", "Tracking-only\nout-of-sample R\u00b2", "Tracking redundant\nwith 40 / weight /\nvertical (R\u00b2)", "Tracking\ntest-retest\n(median SB)*", "Drills with a\nsingle attempt\n(share)", "Outcome\nreliability\n(split-half)"]
M = np.array([[fam[g]["r2_base"], fam[g]["r2_trk_only"], r[g]["flags"]["redundancy_median_R2"], r[g]["flags"]["reliability_median_sb"], r[g]["flags"]["single_attempt_drills"] / r[g]["flags"]["n_drills"], rel_out[g]] for g in order], float)
fig, ax = plt.subplots(figsize=(11.5, 4.3)); good = np.array([[1, 1, 0, 1, 0, 1]] * 4)    # direction for coloring (1=higher better)
for i in range(4):
    for j in range(6):
        v = M[i, j]; score = np.clip(v if good[i, j] else 1 - v, -0.2, 1); ax.add_patch(plt.Rectangle((j, 3 - i), 1, 1, color=plt.cm.Blues(0.15 + 0.7 * max(score, 0)), ec="white", lw=2))
        ax.text(j + .5, 3 - i + .5, f"{v:.2f}", ha="center", va="center", fontsize=12, fontweight="bold", color=("white" if max(score, 0) > 0.55 else "k"))
ax.set_xlim(0, 6); ax.set_ylim(0, 4); ax.set_xticks(np.arange(6) + .5); ax.set_xticklabels(cols, fontsize=8.5); ax.xaxis.tick_top(); ax.set_yticks(np.arange(4) + .5); ax.set_yticklabels([names[g].replace("\n", " ") for g in order[::-1]], fontsize=8.5)
ax.tick_params(length=0); [s.set_visible(False) for s in ax.spines.values()]
fig.text(0.01, 0.01, "*Spearman-Brown test-retest across attempts, only for drills with 2+ attempts. Darker blue = more favourable for detecting a tracking effect. Negative R\u00b2 = worse than predicting the mean.\nDL outcome reliability uses the empirical-Bayes formula (0.94; not clustering-adjusted); WR/OL/DB use game-parity split-half.", fontsize=7, color=C["grey"])
fig.tight_layout(rect=[0, 0.07, 1, 1]); fig.savefig("reports/figures/fig2_why_diagnostics.png", dpi=200); plt.close(fig); print("figures ok", M.round(2).tolist())
