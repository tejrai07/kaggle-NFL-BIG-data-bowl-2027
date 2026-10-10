# NFL Big Data Bowl 2027 entry — status: multi-group analysis complete; notebook/writeup/literature review NOT started
Read in order: reports/competition_requirements.md, data_inventory.md, analysis_plan.md (DL, frozen), multigroup_analysis_plan.md (pre-specified), results.md (DL), results_multigroup.md, limitations.md.
Run (Kaggle path /kaggle/input/nfl-big-data-bowl-2027 or local raw dir; scripts currently use /home/claude/data/raw — edit R in scripts):
scripts/build_ingame_dl.py -> run_analysis_dl.py (frozen) ; build_combine_features.py -> build_outcomes_mg.py -> build_ingame_db.py -> run_multigroup.py -> make_figures_mg.py
Tests: python -c "import sys;sys.path[:0]=['src','tests'];..." (see tests/*.py; plain functions, no pytest installed here).

## Novelty review stage (2026-10-09)
reports/verified_primary_results.md, literature_review.md, novelty_matrix.md, final_research_decision.md, power_followup.json (scripts/power_followup.py, synthetic). Decision: Path A (no additional test). Frozen files re-verified by hash.
