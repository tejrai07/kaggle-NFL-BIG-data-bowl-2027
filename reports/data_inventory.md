# Data inventory — verified against the actual CSVs (run 2026-10-09; auto-generated column tables are in schema_tables.md / schema_report.json)

## Row counts: documentation vs actual
| File | Documented | Actual |
|---|---|---|
| players / combine_results / player_career_successes | 510 | 510 (identical nfl_id sets) |
| combine_tracking | 463,189 | 463,189 (6,310 attempts, 510 players; 431,094 PLAYER + 32,095 BALL rows) |
| player_play | 316,338 | **314,197** (no duplicate keys; all game_id/nfl_id join to games/players) |
| games | 1,002 | 1,002 (per season: 272 REG, 13 POST, **49 PRE**) |
| game_tracking_2023/24/25 | 1.42M / 3.04M / 4.34M | **3.67M / 7.83M / 11.16M** (documentation row counts are not what the files contain) |

## Join map (verified)
players, combine_results, career: 1:1 on nfl_id. combine_tracking: event_id = one attempt of one player (no event has >1 player). player_play -> games on game_id (many:1), -> players on nfl_id.
game_tracking: key (game_id, play_id, nfl_id, time); no duplicate keys in the chunk inspected; frames are exactly 0.1 s apart; `ball_snap` event present for 99.9% of selected DL plays.

## Findings that change the analysis
1. **Preseason (PRE) and playoff games are in player_play and tracking**; 51k PRE rows. Regular season only used for outcomes. 240,412 valid REG player-plays from 401 of 510 players (109 never appear in REG).
2. 12,490 plays are nullified by penalty (excluded).
3. Combine `a` is an acceleration **magnitude** (min 0.0) -> cannot give braking; velocity/acceleration are recomputed from x,y. `dir` 90 deg = +x (verified on 40-yard dash).
4. Combine position groups: WR 107, DB 122, DL 118, OL 121, TE 42 (+ small LB drill set of 4 players). Official times missing: forty 17%, 3-cone 65%, shuttle 61%, bench 62%.
5. Position drills have no stopwatch; 40-yard dash tracking covers 418 players vs 424 with official forty (tracking adds almost no coverage for the 40).
6. Drill names change by year: LINE/LINE_DRILL, PASS_PRO-MIRROR_DRILL/PASS_PRO_MIRROR_DRILL, SPEED_OUT_LEFT/SPEED_OUT_ROUTE_LEFT, OVER_SHOULDER_ADJUST/OVER_THE_SHOULDER_ADJUST, SHORT_ZONE_BREAKS vs three 2025-only variants, CIRCUS_ROUTE_LEFT 2025 only. Not pooled without harmonization.
7. Many drills have one attempt per player (e.g., FOUR_BAG, BODY_CONTROL for DL) -> test-retest not estimable there.
8. Outcome null semantics: separation_at_pass_forward only for route runners; pressure_allowed only OL; player_get_off only DL/edge (incl. run plays, 24%); time_to_pressure non-null only when pressure occurred (null != 0; denominator = rush snaps).
9. Players with >=100 relevant REG snaps: DL 69 (25/23/21 by class), OL 66, WR 63 (29/19/15), DB 57, TE 21.
