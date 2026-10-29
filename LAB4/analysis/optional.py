import numpy as np
import matplotlib.pyplot as plt

d = np.load("route.npz")
st = np.load("stops.npz")
v = np.load("velocity.npz")["v"]
t, acc, gyr = d["t"], d["acc"], d["gyr"]
stopped, bias_gz = st["stopped"], st["bias_gz"]
ay, gz = acc[:, 1], gyr[:, 2] - bias_gz
fs = 1 / np.median(np.diff(t))

def lowpass(x, fc, fs):
    K = np.tan(np.pi * fc / fs); b = K / (1 + K); a1 = (K - 1) / (K + 1)
    out = np.empty_like(x); out[0] = x[0]
    for n in range(1, len(x)):
        out[n] = b * (x[n] + x[n-1]) - a1 * out[n-1]
    return out

def filtfilt(x, fc, fs):
    return lowpass(lowpass(x, fc, fs)[::-1], fc, fs)[::-1]

edges = np.flatnonzero(np.diff(np.r_[0, stopped.astype(int), 0]))
t_stop, off_stop = [], []
for a, b in zip(edges[::2], edges[1::2]):
    if t[b-1] - t[a] > 2:
        t_stop.append(t[(a + b) // 2])
        off_stop.append(ay[a:b].mean())
y_obs = filtfilt(ay - np.interp(t, t_stop, off_stop), 1.0, fs)

w_xdot = filtfilt(gz * v, 1.0, fs)                 
w_dot = np.gradient(filtfilt(gz, 1.0, fs), t)      
resid = y_obs - w_xdot                             

resid_hp = resid - filtfilt(resid, 0.05, fs)
w_dot_hp = w_dot - filtfilt(w_dot, 0.05, fs)

w_s = filtfilt(gz, 1.0, fs)
use = (v > 1) & (np.abs(w_s) > 0.05)
xc = np.sum(w_dot_hp[use] * resid_hp[use]) / np.sum(w_dot_hp[use]**2)
fit = xc * w_dot_hp[use]
r2 = 1 - np.sum((resid_hp[use] - fit)**2) / np.sum((resid_hp[use] - resid_hp[use].mean())**2)
print("Samples used (turning):", use.sum())
print("Estimated x_c (m):", xc)
print("R^2 of the fit:", r2)
moving = use                                    
resid, w_dot = resid_hp, w_dot_hp

fig, axs = plt.subplots(1, 2, figsize=(14, 5))
axs[0].scatter(w_dot[moving], resid[moving], s=1, alpha=0.3)
xs = np.linspace(w_dot[moving].min(), w_dot[moving].max(), 2)
axs[0].plot(xs, xc * xs, "r", lw=2, label=f"fit: x_c = {xc:.2f} m")
axs[0].set_xlabel("ω̇ (rad/s²)"); axs[0].set_ylabel("y_obs − ω·Ẋ (m/s²)")
axs[0].set_title("Residual vs ω̇ (slope = x_c)"); axs[0].legend(); axs[0].grid()
axs[1].plot(t, resid, lw=0.6, label="y_obs − ω·Ẋ")
axs[1].plot(t, xc * w_dot, lw=0.8, label="ω̇·x_c")
axs[1].set_xlabel("time (s)"); axs[1].set_ylabel("m/s²")
axs[1].set_title("Residual and fitted ω̇·x_c over time"); axs[1].legend(); axs[1].grid()
plt.tight_layout(); plt.show()