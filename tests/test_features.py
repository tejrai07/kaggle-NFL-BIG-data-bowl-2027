import numpy as np, pandas as pd, sys; sys.path.insert(0, "src")
from features import attempt_features, frame_interval
def test_constant_speed_line():
    t = np.arange(0, 3, 0.1); f = attempt_features(5.0 * t, np.zeros_like(t))
    assert abs(f["peak_speed"] - 5.0) < 1e-6 and abs(f["path_len"] - 5.0 * 2.9) < 1e-6
def test_braking_negative_and_not_magnitude():
    t = np.arange(0, 3, 0.1); x = 8 * t - 0.5 * 3 * t**2          # decelerating at 3 yd/s^2, speed stays >0
    f = attempt_features(x, np.zeros_like(t)); assert -3.3 < f["peak_brake"] < -2.7
def test_turn_rate_circle():
    t = np.arange(0, 4, 0.1); w = 1.0; f = attempt_features(5*np.cos(w*t), 5*np.sin(w*t))
    assert abs(f["max_turn_rate"] - 1.0) < 0.1 and abs(f["peak_speed"] - 5.0) < 0.2
def test_frame_interval():
    assert abs(frame_interval(pd.Series(pd.date_range("2025-01-01", periods=5, freq="100ms"))) - 0.1) < 1e-9
