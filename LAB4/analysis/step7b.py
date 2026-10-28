import numpy as np
import matplotlib.pyplot as plt

d = np.load("lab4_data.npz")
t, tg, east, north = d["t"], d["tg"], d["east"], d["north"]
v = np.load("velocity.npz")["v"]
yaw_cf = np.load("yaw_cf.npz")["yaw_cf"]                    

def cumtrapz(y, x):
    return np.concatenate([[0], np.cumsum(0.5 * (y[1:] + y[:-1]) * np.diff(x))])

DECLINATION = -14.0
psi = np.radians(yaw_cf + DECLINATION)

xe = cumtrapz(v * np.sin(psi), t)
xn = cumtrapz(v * np.cos(psi), t)

T_ALIGN = (108, 118)
ga, gb = np.searchsorted(tg, T_ALIGN)
ia, ib = np.searchsorted(t, T_ALIGN)
gps_dir = np.arctan2(east[gb] - east[ga], north[gb] - north[ga])
imu_dir = np.arctan2(xe[ib] - xe[ia], xn[ib] - xn[ia])
rot = gps_dir - imu_dir
xe_a = np.cos(rot) * xe + np.sin(rot) * xn
xn_a = -np.sin(rot) * xe + np.cos(rot) * xn
print("Alignment rotation (deg):", np.degrees(rot))

L_gps = np.sum(np.hypot(np.diff(east), np.diff(north)))
L_imu = np.sum(np.hypot(np.diff(xe_a), np.diff(xn_a)))
scale = L_gps / L_imu
print(f"Path length GPS {L_gps:.0f} m, IMU {L_imu:.0f} m -> scale {scale:.3f}")

plt.figure(figsize=(8, 8))
plt.plot(east, north, "k", lw=2, label="GPS")
plt.plot(xe_a, xn_a, "tab:orange", label="IMU dead reckoning")
plt.plot(xe_a * scale, xn_a * scale, "tab:blue", ls="--",
         label=f"IMU dead reckoning × {scale:.2f}")
plt.plot(0, 0, "go", ms=8, label="Start")
plt.xlabel("East (m)"); plt.ylabel("North (m)")
plt.title(f"Trajectory (aligned by {np.degrees(rot):.1f}°)")
plt.axis("equal"); plt.grid(); plt.legend()
plt.tight_layout(); plt.show()