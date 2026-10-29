import numpy as np
import matplotlib.pyplot as plt

c = np.load("circles.npz")
mx, my = c["mag"][:, 0], c["mag"][:, 1]

# Fit ellipse 
M = np.column_stack([mx**2, mx*my, my**2, mx, my])
A, B, C, D, E = np.linalg.lstsq(M, np.ones_like(mx), rcond=None)[0]

# Hard iron
Q = np.array([[A, B/2], [B/2, C]])
center = -0.5 * np.linalg.solve(Q, [D, E])

# Soft iron
k = 1 + center @ Q @ center
w, V = np.linalg.eigh(Q / k)
radii = 1 / np.sqrt(w)
R = radii.mean()
S = V @ np.diag(R / radii) @ V.T

corrected = (S @ (np.column_stack([mx, my]) - center).T).T

print("Hard-iron offset (G):", center)
print("Ellipse semi-axes (G):", radii)
print("Circle radius after correction (G):", R)
print("Soft-iron matrix S:\n", S)
np.savez("mag_cal.npz", center=center, S=S)

fig, ax = plt.subplots(1, 2, figsize=(12, 5.5))
ax[0].scatter(mx, my, s=2)
ax[0].plot(*center, "r+", ms=12, mew=2, label="fitted center")
ax[0].plot(0, 0, "k+", ms=12, mew=2, label="origin")
ax[0].set_title("Before calibration")
ax[1].scatter(corrected[:, 0], corrected[:, 1], s=2, c="tab:green")
ax[1].plot(0, 0, "k+", ms=12, mew=2, label="origin")
ax[1].set_title("After hard- and soft-iron correction")
for a in ax:
    a.set_xlabel("Mag X (G)"); a.set_ylabel("Mag Y (G)")
    a.axis("equal"); a.grid(); a.legend()
plt.tight_layout(); plt.show()