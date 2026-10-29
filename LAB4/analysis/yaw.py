import numpy as np
import matplotlib.pyplot as plt

d = np.load("route.npz")
cal = np.load("mag_cal.npz")
st = np.load("stops.npz")
t, mag, gz = d["t"], d["mag"], d["gyr"][:, 2]
center, S, bias_gz = cal["center"], cal["S"], st["bias_gz"]

wrap = lambda a: (a + 180) % 360 - 180

def cumtrapz(y, x):
    return np.concatenate([[0], np.cumsum(0.5 * (y[1:] + y[:-1]) * np.diff(x))])

# Magnetometer yaw 
mc = (S @ (mag[:, :2] - center).T).T
yaw_mag = np.degrees(np.arctan2(-mc[:, 1], mc[:, 0]))

# Gyro yaw 
yaw_gyro = np.degrees(cumtrapz(gz - bias_gz, t)) + yaw_mag[0]

print("Gyro z bias used (rad/s):", bias_gz)
print("Starting yaw (deg):", yaw_mag[0])
print("Total gyro yaw change (deg):", yaw_gyro[-1] - yaw_gyro[0])

np.savez("yaw.npz", yaw_mag=yaw_mag, yaw_gyro=yaw_gyro)

plt.figure(figsize=(13, 4.5))
plt.plot(t, yaw_mag, lw=0.8, label="Mag yaw (calibrated)")
plt.plot(t, wrap(yaw_gyro), lw=0.8, label="Gyro yaw (integrated)")
plt.xlabel("time (s)"); plt.ylabel("yaw (deg)")
plt.title("Yaw: magnetometer vs integrated gyro")
plt.legend(); plt.grid(); plt.tight_layout(); plt.show()