import numpy as np
import matplotlib.pyplot as plt

d = np.load("route.npz")
t, acc, gyr = d["t"], d["acc"], d["gyr"]
ax_, gz = acc[:, 0], gyr[:, 2]

# Finding IMU stops
W = 40                                         
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

edges = np.flatnonzero(np.diff(np.r_[0, stopped.astype(int), 0]))
starts, ends = edges[::2], edges[1::2]
print("Number of stops:", len(starts))
print("Time stopped (s):", round(stopped.sum() / 40, 1),
      f"({100 * stopped.mean():.1f}% of the route)")

# Biases 
bias_gz = gz[stopped].mean()                   # all stops
bias_ax = ax_[starts[0]:ends[0]].mean()        # first stop
print("First stop: t =", round(t[starts[0]], 1), "to", round(t[ends[0] - 1], 1), "s")
print("Gyro z bias (rad/s):", bias_gz)
print("Accel x bias (m/s^2):", bias_ax)

cdat = np.load("circles.npz")
ct, cay, cgz = cdat["t"], cdat["acc"][:, 1], cdat["gyr"][:, 2]
last = ct >= ct[-1] - 10                       
k5 = np.ones(20) / 20                          
ay_s = np.convolve(cay, k5, "same")[last]
gz_s = np.convolve(cgz, k5, "same")[last]
v0 = ay_s.mean() / gz_s.mean()
print("Starting speed v0 (m/s):", v0)

np.savez("stops.npz", stopped=stopped, bias_gz=bias_gz, bias_ax=bias_ax, v0=v0)

# Plot
fig, axs = plt.subplots(2, 1, figsize=(13, 6), sharex=True)
axs[0].plot(t, gz, lw=0.5)
axs[0].set_ylabel("gyro z (rad/s)")
axs[1].plot(t, std_ax, lw=0.5)
axs[1].axhline(0.05, color="r", ls="--", label="threshold")
axs[1].set_ylabel("1 s std of accel x"); axs[1].set_xlabel("time (s)")
for a in axs:
    for s0, e0 in zip(starts, ends):
        a.axvspan(t[s0], t[e0 - 1], color="tab:green", alpha=0.25)
    a.grid()
axs[0].set_title("Detected stops (green)")
axs[1].legend()
plt.tight_layout(); plt.show()