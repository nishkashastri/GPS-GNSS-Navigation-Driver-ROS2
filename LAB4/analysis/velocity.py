import numpy as np
import matplotlib.pyplot as plt

d = np.load("route.npz")
st = np.load("stops.npz")
t, acc = d["t"], d["acc"]
tg, east, north = d["tg"], d["east"], d["north"]
stopped, bias_ax, v0 = st["stopped"], st["bias_ax"], st["v0"]
ax_ = acc[:, 0]
N = len(t)

def cumtrapz(y, x):
    return np.concatenate([[0], np.cumsum(0.5 * (y[1:] + y[:-1]) * np.diff(x))])

# GPS speed 
dtg = np.diff(tg)
v_gps = np.hypot(np.diff(east), np.diff(north)) / dtg
tv = tg[:-1] + dtg / 2
good = v_gps < 20                         
v_gps, tv = v_gps[good], tv[good]
print("Max GPS speed after cleanup (m/s):", v_gps.max())

# Raw integration 
v_raw = cumtrapz(ax_, t)
print("Raw IMU velocity at end (m/s):", v_raw[-1])

# Adjusted 
a1 = ax_ - bias_ax                        
print("Accel x bias (m/s^2):", bias_ax, "  v0 (m/s):", v0)

v = np.zeros_like(t)                      
i = 0
while i < N:
    if stopped[i]:
        i += 1
        continue
    j = i
    while j < N and not stopped[j]:
        j += 1
    seg = slice(i, j)
    vs = cumtrapz(a1[seg], t[seg])
    if i == 0:
        vs = vs + v0                      
    if j < N and j - i > 1:               
        vs = vs - vs[-1] * (t[seg] - t[i]) / (t[j-1] - t[i])
    v[seg] = vs
    i = j

v = np.clip(v, 0, None)                   

vg_i = np.interp(t, tv, v_gps)
print("RMS difference IMU vs GPS (m/s):", np.sqrt(np.mean((v - vg_i)**2)))

np.savez("velocity.npz", v=v)

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
plt.tight_layout; plt.show()