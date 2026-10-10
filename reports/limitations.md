# Limitations (current, after multi-group stage)
- Sample: 59-66 players per group, three draft classes; leave-one-class-out R^2 and bootstrap CIs are noisy; bootstrap holds LOCO predictions fixed (approximation); permutation tests have limited power (CI half-widths 0.03-0.12 R^2).
- Exposure: 2023 class has up to 3 seasons, 2025 class 1; rookie-only sensitivity exists but with fewer snaps.
- Features: 4 coarse cross-drill composites chosen in advance; drill-phase features (e.g. first step in a specific drill, break mechanics in specific routes) were NOT tested. Most drills have a single attempt, so test-retest is estimable for only 12 (WR), 4 (OL), 8 (DB), 4 (DL) drill x feature cells.
- Outcomes: WR separation depends on route concept, coverage and throw timing; OL pressure allowed depends on QB/scheme/teammates and has split-half reliability 0.40; DB outcome is physical top speed in coverage on plays with a throw (about 10k candidate snaps excluded), NOT coverage performance, which cannot be measured from these data.
- EB variance formula ignores game/team clustering (reliability formula is optimistic; split-half by game parity reported).
- Frozen DL baseline (11 variables, fixed lambda) overfit; post hoc parsimonious/nested variants are labelled as such.
- Only regular-season, non-nullified plays; preseason/playoffs excluded; players without enough snaps excluded (selection into playing time).
- Novelty literature search NOT done; no originality claim. No notebook or writeup yet.
- Sensitivity analyses: two CIs exclude zero (WR rookie-only: tracking hurts; OL best-attempt: +0.076); exploratory, not findings.
