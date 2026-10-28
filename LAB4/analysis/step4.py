import numpy as np
import matplotlib.pyplot as plt

d = np.load("lab4_data.npz")
cal = np.load("mag_cal.npz")
t, mag, gyr = d["t"], d["mag"], d["gyr"]
center, S = cal["center"], cal["S"]

wrap = lambda a: (a + 180) % 360 - 180     

# Mag yaw
mc = (S @ (mag[:, :2] - center).T).T
yaw_mag = np.degrees(np.arctan2(-mc[:, 1], mc[:, 0]))

# Gyro yaw
gz = gyr[:, 2]
bias = gz[t < 15].mean()
print("Gyro z bias (rad/s):", bias)
r = gz - bias
integral = np.concatenate([[0], np.cumsum(0.5 * (r[1:] + r[:-1]) * np.diff(t))])
yaw_gyro = np.degrees(integral) + yaw_mag[0]

np.savez("yaw.npz", yaw_mag=yaw_mag, yaw_gyro=yaw_gyro)

# Plot
plt.figure(figsize=(13, 4.5))
plt.plot(t, yaw_mag, label="Mag yaw (calibrated)", lw=0.8)
plt.plot(t, wrap(yaw_gyro), label="Gyro yaw (integrated)", lw=0.8)
plt.xlabel("time (s)"); plt.ylabel("yaw (deg)")
plt.legend(); plt.grid(); plt.tight_layout(); plt.show()