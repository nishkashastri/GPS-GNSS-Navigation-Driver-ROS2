import numpy as np
import matplotlib.pyplot as plt

d = np.load("lab4_data.npz")
t, mag = d["t"], d["mag"]

# 1. Take only the circle data
sel = (t >= 25) & (t <= 88)
mx, my = mag[sel, 0], mag[sel, 1]

# 2. Fit an ellipse:  A x² + B xy + C y² + D x + E y = 1   (least squares)
M = np.column_stack([mx**2, mx*my, my**2, mx, my])
A, B, C, D, E = np.linalg.lstsq(M, np.ones_like(mx), rcond=None)[0]

# 3. Hard iron = ellipse center
Q = np.array([[A, B/2], [B/2, C]])
center = -0.5 * np.linalg.solve(Q, [D, E])

# 4. Soft iron = make the ellipse a circle
k = 1 + center @ Q @ center
w, V = np.linalg.eigh(Q / k)        # V = ellipse axis directions
radii = 1 / np.sqrt(w)              # ellipse semi-axis lengths
R = radii.mean()                    # target circle radius
S = V @ np.diag(R / radii) @ V.T    # rotate -> scale -> rotate back

print("Hard-iron offset (G):", center)
print("Ellipse semi-axes (G):", radii)
print("Soft-iron matrix:\n", S)

# 5. Apply correction to the circle data
corrected = (S @ (np.column_stack([mx, my]) - center).T).T

# 6. Plot before / after
fig, ax = plt.subplots(1, 2, figsize=(12, 5.5))
ax[0].scatter(mx, my, s=2)
ax[0].plot(*center, "r+", ms=15, mew=2)
ax[0].set_title("Before calibration")
ax[1].scatter(corrected[:, 0], corrected[:, 1], s=2, c="g")
ax[1].plot(0, 0, "k+", ms=15, mew=2)
ax[1].set_title("After hard + soft iron correction")
for a in ax:
    a.set_xlabel("Mag X (Gauss)"); a.set_ylabel("Mag Y (Gauss)")
    a.axis("equal"); a.grid()
plt.tight_layout(); plt.show()  
np.savez("mag_cal.npz", center=center, S=S)
