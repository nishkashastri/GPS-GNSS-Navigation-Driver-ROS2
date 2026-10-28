import numpy as np
import matplotlib.pyplot as plt

d = np.load("lab4_data.npz")
y = np.load("yaw.npz")
t, yaw_vn = d["t"], d["yaw"]
yaw_mag, yaw_gyro = y["yaw_mag"], y["yaw_gyro"]

wrap = lambda a: (a + 180) % 360 - 180                
U = lambda a: np.degrees(np.unwrap(np.radians(a)))    
fs = 1 / np.median(np.diff(t))                        

def lowpass(x, fc, fs):
    K = np.tan(np.pi * fc / fs)
    b = K / (1 + K)
    a1 = (K - 1) / (K + 1)
    out = np.empty_like(x)
    out[0] = x[0]
    for n in range(1, len(x)):
        out[n] = b * (x[n] + x[n-1]) - a1 * out[n-1]
    return out

def filtfilt(x, fc, fs):
    return lowpass(lowpass(x, fc, fs)[::-1], fc, fs)[::-1]

# Complementary filter 
FC = 0.05              
err = wrap(yaw_mag - yaw_gyro)
yaw_cf = wrap(yaw_gyro + filtfilt(err, FC, fs))

# Results 
offset = np.median(wrap(yaw_cf - yaw_vn))
print("Sample rate (Hz):", fs)
print("Median offset ours - VN-100 (deg):", offset)

print("Total yaw change (deg):")
print("  mag   :", U(yaw_mag)[-1] - U(yaw_mag)[0])
print("  gyro  :", yaw_gyro[-1] - yaw_gyro[0])
print("  ours  :", U(yaw_cf)[-1] - U(yaw_cf)[0])
print("  VN-100:", U(yaw_vn)[-1] - U(yaw_vn)[0])

np.savez("yaw_cf.npz", yaw_cf=yaw_cf)

# Plots 
fig, ax = plt.subplots(2, 1, figsize=(13, 8), sharex=True)

ax[0].plot(t, U(yaw_mag), lw=0.5, alpha=0.5, label="Mag yaw (naive unwrap)")
ax[0].plot(t, yaw_gyro, lw=0.8, label="Gyro yaw")
ax[0].plot(t, U(yaw_cf), "k", lw=1, label="Complementary filter")
ax[0].set_title(f"Unwrapped yaw, complementary filter (fc = {FC} Hz)")

ax[1].plot(t, U(yaw_cf), "k", lw=1, label="Ours")
ax[1].plot(t, U(yaw_vn) + offset, "r", lw=1, label=f"VN-100 yaw + {offset:.0f}°")
ax[1].set_title("Our yaw vs IMU's own yaw (unwrapped, VN-100 shifted by median offset)")
ax[1].set_xlabel("time (s)")

for a in ax:
    a.set_ylabel("yaw (deg)"); a.legend(); a.grid()
plt.tight_layout(); plt.show()