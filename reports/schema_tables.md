# Data inventory (auto-generated)

## combine_results.csv
rows: 510

| column | dtype | nulls |
|---|---|---|
| draft_year | int64 | 0 |
| nfl_id | int64 | 0 |
| combine_position | str | 0 |
| combine_height | float64 | 0 |
| combine_weight | int64 | 0 |
| hand_size | float64 | 0 |
| arm_length | float64 | 0 |
| wing_span | float64 | 0 |
| ten_yd_split | float64 | 85 |
| forty | float64 | 86 |
| vertical | float64 | 72 |
| broad_jump | float64 | 87 |
| three_cone | float64 | 330 |
| short_shuttle | float64 | 309 |
| bench_reps | float64 | 318 |
| ngs_athleticism_score | int64 | 0 |
| ngs_college_production_score | float64 | 1 |
| ngs_final_score | float64 | 1 |

## combine_tracking.csv
rows: 463,189

| column | dtype | nulls |
|---|---|---|
| draft_year | int64 | 0 |
| event_id | str | 0 |
| nfl_id | int64 | 0 |
| entity_type | str | 0 |
| time | str | 0 |
| drill_type | str | 0 |
| drill_name | str | 0 |
| attempt | int64 | 0 |
| x | float64 | 0 |
| y | float64 | 0 |
| s | float64 | 0 |
| a | float64 | 0 |
| dis | float64 | 0 |
| dir | float64 | 0 |

## game_tracking_2023.csv
rows: 3,665,443

| column | dtype | nulls |
|---|---|---|
| game_id | int64 | 0 |
| play_id | int64 | 0 |
| nfl_id | int64 | 0 |
| time | str | 0 |
| x | float64 | 0 |
| y | float64 | 0 |
| s | float64 | 0 |
| a | float64 | 0 |
| dis | float64 | 0 |
| o | float64 | 0 |
| dir | float64 | 0 |
| event | str | 3422066 |

## game_tracking_2024.csv
rows: 7,827,944

| column | dtype | nulls |
|---|---|---|
| game_id | int64 | 0 |
| play_id | int64 | 0 |
| nfl_id | int64 | 0 |
| time | str | 0 |
| x | float64 | 0 |
| y | float64 | 0 |
| s | float64 | 0 |
| a | float64 | 0 |
| dis | float64 | 0 |
| o | float64 | 0 |
| dir | float64 | 0 |
| event | str | 7306249 |

## game_tracking_2025.csv
rows: 11,160,903

| column | dtype | nulls |
|---|---|---|
| game_id | int64 | 0 |
| play_id | int64 | 0 |
| nfl_id | int64 | 0 |
| time | str | 0 |
| x | float64 | 0 |
| y | float64 | 0 |
| s | float64 | 0 |
| a | float64 | 0 |
| dis | float64 | 0 |
| o | float64 | 0 |
| dir | float64 | 0 |
| event | str | 10425238 |

## games.csv
rows: 1,002

| column | dtype | nulls |
|---|---|---|
| game_id | int64 | 0 |
| game_key | int64 | 0 |
| season | int64 | 0 |
| season_type | str | 0 |
| week | int64 | 0 |
| home_team_abbr | str | 0 |
| visitor_team_abbr | str | 0 |

## player_career_successes.csv
rows: 510

| column | dtype | nulls |
|---|---|---|
| nfl_id | int64 | 0 |
| career_offensive_snaps | int64 | 0 |
| career_defensive_snaps | int64 | 0 |
| career_special_teams_snaps | int64 | 0 |
| career_games_active | int64 | 0 |
| career_games_started | int64 | 0 |
| ap_all_pro_1st_team | int64 | 0 |
| ap_all_pro_2nd_team | int64 | 0 |
| pro_bowl_original_ballot | int64 | 0 |

## player_play.csv
rows: 314,197

| column | dtype | nulls |
|---|---|---|
| game_id | int64 | 0 |
| play_id | int64 | 0 |
| team_abbr | str | 0 |
| nfl_id | int64 | 0 |
| lined_up_position | str | 1383 |
| play_description | str | 0 |
| quarter | int64 | 0 |
| down | int64 | 0 |
| yards_to_go | int64 | 0 |
| possession_team | str | 0 |
| yardline_side | str | 4102 |
| yardline_number | int64 | 0 |
| game_clock | str | 0 |
| pre_snap_home_score | int64 | 0 |
| pre_snap_visitor_score | int64 | 0 |
| play_direction | str | 50 |
| pre_snap_home_team_win_probability | float64 | 3 |
| pre_snap_visitor_team_win_probability | float64 | 3 |
| home_team_win_probability_added | float64 | 6 |
| visitor_team_win_probility_added | float64 | 6 |
| expected_points_added | float64 | 0 |
| expected_points | float64 | 0 |
| offense_formation | str | 5335 |
| receiver_alignment | str | 4597 |
| pass_result | str | 103636 |
| pass_length | float64 | 129458 |
| play_nullified_by_penalty | str | 0 |
| penalty_yards | float64 | 293447 |
| pre_penalty_yards_gained | int64 | 0 |
| yards_gained | int64 | 0 |
| team_coverage_man_zone | str | 38919 |
| team_coverage_type | str | 38919 |
| in_motion_at_ball_snap | object | 158231 |
| target | bool | 0 |
| rec_yards | float64 | 307937 |
| rush_yards | float64 | 314175 |
| yards_after_catch | float64 | 307937 |
| fumble | float64 | 314124 |
| fumble_lost | float64 | 314124 |
| route_ran | str | 260889 |
| separation_at_pass_forward | float64 | 267460 |
| cushion | float64 | 210445 |
| expected_yards_after_catch | float64 | 305221 |
| dropback_duration | float64 | 253394 |
| extended_sack_allowed | float64 | 253394 |
| pass_rushers_encountered | float64 | 253394 |
| peak_pressure_probability_allowed | float64 | 256169 |
| pressure_allowed | object | 253394 |
| sack_allowed | float64 | 253394 |
| time_to_pressure_allowed | float64 | 309227 |
| quick_pressure | object | 310434 |
| unblocked_pressure | object | 227359 |
| blitzing | object | 113470 |
| player_get_off | float64 | 270195 |
| sack | float64 | 227362 |
| tackle | float64 | 302301 |
| assist | float64 | 302301 |
| caused_forced_fumble | float64 | 302301 |
| recovered_fumble | object | 311983 |
| tackle_for_loss | object | 302301 |
| time_to_pressure | float64 | 310393 |
| time_to_qb_hurry | float64 | 310318 |
| coverage_assignment | str | 241545 |
| coverage_assignment_at_snap | str | 242072 |

## players.csv
rows: 510

| column | dtype | nulls |
|---|---|---|
| nfl_id | int64 | 0 |
| display_name | str | 0 |
| draft_year | int64 | 0 |
| nfl_position | str | 0 |
| birth_date | str | 0 |
| college_name | str | 0 |
| college_conference | str | 0 |
| draft_round | float64 | 127 |
| draft_pick_within_round | float64 | 127 |
| draft_overall_pick | float64 | 127 |

