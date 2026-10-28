import numpy as np
import matplotlib.pyplot as plt

d = np.load("lab4_data.npz")
t, acc = d["t"], d["acc"]
tg, east, north = d["tg"], d["east"], d["north"]
ax_ = acc[:, 0]                                   

def cumtrapz(y, x):                               
    return np.concatenate([[0], np.cumsum(0.5 * (y[1:] + y[:-1]) * np.diff(x))])

dtg = np.diff(tg)
v_gps = np.hypot(np.diff(east), np.diff(north)) / dtg
tv = tg[:-1] + dtg / 2  
good = v_gps < 20       
v_gps, tv = v_gps[good], tv[good]
print("Max GPS speed after cleanup (m/s):", v_gps.max())

v_raw = cumtrapz(ax_, t)
print("Raw IMU velocity at end (m/s):", v_raw[-1])

bias = ax_[t < 15].mean()
a1 = ax_ - bias
print("Accel x bias (m/s^2):", bias)

gz = d["gyr"][:, 2]
W = 40                                          
k = np.ones(W) / W
mean_ax = np.convolve(ax_, k, "same")
std_ax = np.sqrt(np.maximum(np.convolve(ax_**2, k, "same") - mean_ax**2, 0))
mean_gz = np.abs(np.convolve(gz, k, "same"))
stopped = (std_ax < 0.05) & (mean_gz < 0.02)

edges = np.flatnonzero(np.diff(np.r_[0, stopped.astype(int), 0]))
for a, b in zip(edges[::2], edges[1::2]):
    if t[min(b, len(t) - 1)] - t[a] < 2:
        stopped[a:b] = False
print("Fraction of time stopped:", stopped.mean())

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
    if j < N and j - i > 1:                     
        vs = vs - vs[-1] * (t[seg] - t[i]) / (t[j-1] - t[i])
    v[seg] = vs
    i = j

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