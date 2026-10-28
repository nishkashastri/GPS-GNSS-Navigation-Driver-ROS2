import numpy as np
import matplotlib.pyplot as plt

d = np.load("lab4_data.npz")
t, acc, gyr = d["t"], d["acc"], d["gyr"]
tg, east, north = d["tg"], d["east"], d["north"]
v = np.load("velocity.npz")["v"]
ay, gz = acc[:, 1], gyr[:, 2]
fs = 1 / np.median(np.diff(t))

def lowpass(x, fc, fs):
    K = np.tan(np.pi * fc / fs); b = K / (1 + K); a1 = (K - 1) / (K + 1)
    out = np.empty_like(x); out[0] = x[0]
    for n in range(1, len(x)):
        out[n] = b * (x[n] + x[n-1]) - a1 * out[n-1]
    return out

def filtfilt(x, fc, fs):
    return lowpass(lowpass(x, fc, fs)[::-1], fc, fs)[::-1]

stopped = np.load("velocity.npz")["stopped"]

# Accel y offset at each stop (longer than 2 s), interpolated between stops
edges = np.flatnonzero(np.diff(stopped.astype(int))) + 1
bounds = np.concatenate([[0], edges, [len(t)]])
t_stop, off_stop = [], []
for a, b in zip(bounds[:-1], bounds[1:]):
    if stopped[a] and t[b-1] - t[a] > 2:
        t_stop.append(t[(a + b) // 2])
        off_stop.append(ay[a:b].mean())
offset = np.interp(t, t_stop, off_stop)
print("Accel y offsets at stops (m/s^2):", np.round(off_stop, 2))

y_obs = filtfilt(ay - offset, 1.0, fs)
w_xdot = filtfilt(gz * v, 1.0, fs)

moving = v > 1
print("Correlation while moving:", np.corrcoef(y_obs[moving], w_xdot[moving])[0, 1])

fig, axs = plt.subplots(2, 1, figsize=(13, 8), sharex=True)
axs[0].plot(t, filtfilt(ay, 1.0, fs), lw=0.8, label="y_obs raw")
axs[0].plot(t, w_xdot, lw=0.8, label="ω·Ẋ")
axs[0].set_title("Before removing stop offset")
axs[1].plot(t, y_obs, lw=0.8, label="y_obs (offset removed)")
axs[1].plot(t, w_xdot, lw=0.8, label="ω·Ẋ")
axs[1].set_title("After removing stop offset")
axs[1].set_xlabel("time (s)")
for a in axs:
    a.set_ylabel("lateral accel (m/s²)"); a.legend(); a.grid()
plt.tight_layout(); plt.show()