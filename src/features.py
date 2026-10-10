"""Kinematic features from 10 Hz x,y tracks. Units: yards, seconds. Frame interval checked, not assumed."""
import numpy as np, pandas as pd
def frame_interval(t: pd.Series) -> float:
    dt = pd.to_datetime(t).diff().dt.total_seconds().dropna()
    return float(dt.median())
def velocity_components(x, y, dt):
    """Central-difference velocity (yd/s) from positions; independent of the dir convention."""
    return np.gradient(np.asarray(x, float), dt), np.gradient(np.asarray(y, float), dt)
def attempt_features(x, y, dt=0.1, smooth=3, trim=3):
    x_raw, y_raw = np.asarray(x, float), np.asarray(y, float)
    x, y = pd.Series(x).rolling(smooth, center=True, min_periods=1).mean(), pd.Series(y).rolling(smooth, center=True, min_periods=1).mean()
    vx, vy = velocity_components(x, y, dt)
    speed = np.hypot(vx, vy)
    ax, ay = np.gradient(vx, dt), np.gradient(vy, dt)
    unit_x, unit_y = vx / np.maximum(speed, 1e-6), vy / np.maximum(speed, 1e-6)
    a_long = ax * unit_x + ay * unit_y              # along direction of motion; negative = braking
    heading = np.unwrap(np.arctan2(vy, vx))
    omega = np.gradient(heading, dt)                # rad/s, only meaningful while moving
    moving = speed > 1.0
    inner = np.zeros(len(x), bool); inner[trim:len(x) - trim] = True   # drop edge frames biased by smoothing/differencing
    moving = moving & inner
    if not inner.any(): inner[:] = True
    return {"peak_speed": float(speed.max()), "peak_accel": float(a_long[inner].max()),
            "peak_brake": float(a_long[moving].min()) if moving.any() else np.nan,
            "path_len": float(np.hypot(np.diff(x_raw), np.diff(y_raw)).sum()),
            "max_turn_rate": float(np.abs(omega[moving]).max()) if moving.any() else np.nan,
            "duration_s": float((len(x) - 1) * dt)}


def drill_features(df):
    """df: one drill attempt, sorted by time, columns x,y. Returns attempt_features dict (direction-free)."""
    return attempt_features(df.x.values, df.y.values, dt=0.1)
