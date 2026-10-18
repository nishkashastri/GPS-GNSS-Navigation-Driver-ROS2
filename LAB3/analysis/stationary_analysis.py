#!/usr/bin/env python3
import os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import norm

df = pd.read_csv(sys.argv[1])
os.makedirs('plots', exist_ok=True)

groups = {
    'Euler angles': (['roll_deg', 'pitch_deg', 'yaw_deg'], 'deg'),
    'Gyroscope':    (['gyro_x', 'gyro_y', 'gyro_z'], 'rad/s'),
    'Accelerometer':(['accel_x', 'accel_y', 'accel_z'], 'm/s²'),
    'Magnetometer': (['mag_x', 'mag_y', 'mag_z'], 'T'),
}

rows = []
for name, (cols, unit) in groups.items():
    # Time series
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    for ax, c in zip(axes, cols):
        ax.plot(df['time'], df[c], linewidth=0.5)
        ax.set_ylabel(f'{c} [{unit}]')
        ax.grid(True)
    axes[-1].set_xlabel('Time [s]')
    fig.suptitle(f'{name} - time series (stationary)')
    fig.tight_layout()
    fig.savefig(f"plots/{name.split()[0].lower()}_timeseries.png", dpi=150)
    plt.close(fig)

    # Histograms with fitted Gaussian
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    for ax, c in zip(axes, cols):
        x = df[c].values
        mu, sd = x.mean(), x.std(ddof=1)
        rows.append([c, unit, mu, sd])
        lo, hi = np.percentile(x, [0.5, 99.5]); ax.hist(x, bins=60, range=(lo, hi), density=True, alpha=0.7, label='data')
        xs = np.linspace(lo, hi, 300)
        ax.plot(xs, norm.pdf(xs, mu, sd), 'r', label='Gaussian fit')
        ax.set_title(f'{c}\nμ={mu:.4g}, σ={sd:.3g}')
        ax.set_xlabel(f'[{unit}]')
        ax.legend(fontsize=8)
    fig.suptitle(f'{name} - histograms (stationary)')
    fig.tight_layout()
    fig.savefig(f"plots/{name.split()[0].lower()}_histogram.png", dpi=150)
    plt.close(fig)

stats = pd.DataFrame(rows, columns=['signal', 'unit', 'mean', 'std'])
stats.to_csv('stationary_stats.csv', index=False)
print(stats.to_string(index=False))
