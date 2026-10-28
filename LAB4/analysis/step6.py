import numpy as np
import matplotlib.pyplot as plt

d = np.load("lab4_data.npz")
t, acc = d["t"], d["acc"]
tg, east, north = d["tg"], d["east"], d["north"]
ax_ = acc[:, 0]                                   # forward accel

def cumtrapz(y, x):                               # trapezoidal integral
    return np.concatenate([[0], np.cumsum(0.5 * (y[1:] + y[:-1]) * np.diff(x))])

# 1. GPS speed
dtg = np.diff(tg)
v_gps = np.hypot(np.diff(east), np.diff(north)) / dtg
tv = tg[:-1] + dtg / 2                            # midpoint times
good = v_gps < 20                                 # drop the position jump
v_gps, tv = v_gps[good], tv[good]
print("Max GPS speed after cleanup (m/s):", v_gps.max())

# 2. Raw integration
v_raw = cumtrapz(ax_, t)
print("Raw IMU velocity at end (m/s):", v_raw[-1])

# 3a. Remove parked bias
bias = ax_[t < 15].mean()
a1 = ax_ - bias
print("Accel x bias (m/s^2):", bias)

# 3b. Find stops from the IMU only
gz = d["gyr"][:, 2]
W = 40                                            # 1 s window at 40 Hz
k = np.ones(W) / W
mean_ax = np.convolve(ax_, k, "same")
std_ax = np.sqrt(np.maximum(np.convolve(ax_**2, k, "same") - mean_ax**2, 0))
mean_gz = np.abs(np.convolve(gz, k, "same"))
stopped = (std_ax < 0.05) & (mean_gz < 0.02)

# keep only stops lasting at least 2 s
edges = np.flatnonzero(np.diff(np.r_[0, stopped.astype(int), 0]))
for a, b in zip(edges[::2], edges[1::2]):
    if t[min(b, len(t) - 1)] - t[a] < 2:
        stopped[a:b] = False
print("Fraction of time stopped:", stopped.mean())

# 3c. Integrate each moving segment, force it to end at 0
v = np.zeros_like(t)
i, N = 0, len(t)
while i < N:
    if stopped[i]:
        i += 1
        continue
    j = i
    while j < N and not stopped[j]:
        j += 1
    seg = slice(i, j)
    vs = cumtrapz(a1[seg], t[seg])
    if j < N and j - i > 1:                       # segment ends at a stop
        vs = vs - vs[-1] * (t[seg] - t[i]) / (t[j-1] - t[i])
    v[seg] = vs
    i = j

# 3d. No reversing
v = np.clip(v, 0, None)

np.savez("velocity.npz", v=v, stopped=stopped)

fig, axs = plt.subplots(2, 1, figsize=(13, 8), sharex=True)
axs[0].plot(t, v_raw, label="IMU: raw integration")
axs[0].plot(tv, v_gps, label="GPS")
axs[0].set_title("Forward velocity BEFORE adjustment")
axs[1].plot(t, v, label="IMU: adjusted")
axs[1].plot(tv, v_gps, alpha=0.8, label="GPS")
axs[1].set_title("Forward velocity AFTER adjustment")
axs[1].set_xlabel("time (s)")
for a in axs:
    a.set_ylabel("speed (m/s)"); a.legend(); a.grid()
plt.tight_layout(); plt.show()