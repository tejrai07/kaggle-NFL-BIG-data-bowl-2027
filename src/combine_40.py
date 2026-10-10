"""40-yard-dash features from 10 Hz tracking. Time to reach cumulative x-distance d from motion onset (linear interpolation)."""
import numpy as np, pandas as pd
def split_times(x, t_s, dists=(5, 10, 20, 30, 40), onset_yd=0.15):
    x = np.asarray(x, float); t = np.asarray(t_s, float)
    prog = x - x[0]
    on = np.argmax(prog > onset_yd)                      # first frame past onset threshold
    if prog[on] <= onset_yd: return {f"t{d}": np.nan for d in dists}
    out = {}
    for d in dists:
        idx = np.argmax(prog >= d)
        if prog[idx] < d: out[f"t{d}"] = np.nan; continue
        t_at = np.interp(d, prog[idx-1:idx+1], t[idx-1:idx+1]) if idx > 0 else t[0]
        t_on = np.interp(onset_yd, prog[max(on-1,0):on+1], t[max(on-1,0):on+1]) if on > 0 else t[0]
        out[f"t{d}"] = float(t_at - t_on)
    return out
def build(ct):
    f = ct[(ct.drill_type == "FORTY_YARD_DASH") & (ct.entity_type == "PLAYER")].copy()
    f["t"] = pd.to_datetime(f.time); f = f.sort_values(["event_id", "t"])
    rows = []
    for ev, e in f.groupby("event_id"):
        ts = (e.t - e.t.iloc[0]).dt.total_seconds().values
        r = split_times(e.x.values, ts); r.update(event_id=ev, nfl_id=int(e.nfl_id.iloc[0]), attempt=int(e.attempt.iloc[0]),
                                                 peak_speed=float(e.s.max()), start_x=float(e.x.iloc[0]), n_frames=len(e))
        rows.append(r)
    return pd.DataFrame(rows)

from scipy.optimize import least_squares
def fit_sprint(x, t_s):
    """Mono-exponential sprint model x(t)=x0+vmax*(u-tau*(1-exp(-u/tau))), u=max(t-t0,0). Onset-free burst (tau) and top speed (vmax).
    Returns vmax (yd/s), tau (s, smaller = faster acceleration), t0 (s), rmse (yd)."""
    x = np.asarray(x, float); t = np.asarray(t_s, float); x0 = x[0]
    def model(p):
        v, tau, t0 = p; u = np.clip(t - t0, 0, None); return x0 + v * (u - tau * (1 - np.exp(-u / tau)))
    best = None
    for t0g in (0.0, 0.3, 0.6):
        r = least_squares(lambda p: model(p) - x, [10.0, 1.2, t0g], bounds=([5, 0.2, -0.5], [15, 4.0, 3.0]))
        if best is None or r.cost < best.cost: best = r
    v, tau, t0 = best.x
    return {"vmax": v, "tau": tau, "t0": t0, "rmse": float(np.sqrt(2 * best.cost / len(x))), "a0": v / tau}
