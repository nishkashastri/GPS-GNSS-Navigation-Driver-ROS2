import csv
import numpy as np
import matplotlib.pyplot as plt

with open('gps_walking_v4.csv', 'r') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Number of rows: {len(rows)}")

eastings = []
northings = []

for row in rows:
    eastings.append(float(row['utm_easting']))
    northings.append(float(row['utm_northing']))

eastings = np.array(eastings)
northings = np.array(northings)

times = np.array([float(row['sec']) for row in rows])
times = times - times[0]  

print(f"First position: ({eastings[0]}, {northings[0]})")
print(f"Last position: ({eastings[-1]}, {northings[-1]})")

# Total straight-line distance covered 
total_displacement = np.sqrt((eastings[-1] - eastings[0])**2 + (northings[-1] - northings[0])**2)
print(f"Straight-line displacement (start to end): {total_displacement:.2f} m")

# Distance traveled between consecutive points
step_distances = np.sqrt(np.diff(eastings)**2 + np.diff(northings)**2)
total_path_length = np.sum(step_distances)
print(f"Total path length (sum of steps): {total_path_length:.2f} m")

step_distances = np.sqrt(np.diff(eastings)**2 + np.diff(northings)**2)
step_times = np.diff(times)

speeds = step_distances / step_times  # meters per second

print(f"Mean step distance: {np.mean(step_distances):.2f} m")
print(f"Mean speed: {np.mean(speeds):.2f} m/s")
print(f"Max speed: {np.max(speeds):.2f} m/s")
print(f"Std deviation of speed: {np.std(speeds):.2f} m/s")

# Scatter plot colored by time — shows the walking trajectory
plt.figure()
sc = plt.scatter(eastings, northings, c=times, cmap='viridis', s=15)
plt.colorbar(sc, label='Time since start (s)')
plt.xlabel('UTM Easting (m)')
plt.ylabel('UTM Northing (m)')
plt.title('Walking GPS Data — Trajectory Colored by Time')
plt.axis('equal')
plt.savefig('walking_scatter_time.png')
print("Saved plot to walking_scatter_time.png")
