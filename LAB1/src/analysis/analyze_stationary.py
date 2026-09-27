import csv
import numpy as np
import matplotlib.pyplot as plt

with open('gps_stationary.csv', 'r') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Number of rows: {len(rows)}")
print(f"First row: {rows[0]}")

eastings = []
northings = []

for row in rows:
    eastings.append(float(row['utm_easting']))
    northings.append(float(row['utm_northing']))   

print(f"First easting: {eastings[0]}")
print(f"First northing: {northings[0]}")

eastings = np.array(eastings)
northings = np.array(northings)

mean_easting = np.mean(eastings)
mean_northing = np.mean(northings)

std_easting = np.std(eastings)
std_northing = np.std(northings)

print(f"Mean position: ({mean_easting}, {mean_northing})")
print(f"Std deviation: ({std_easting}, {std_northing})")

distances = np.sqrt((eastings - mean_easting)**2 + (northings - mean_northing)**2)

mean_distance = np.mean(distances)
max_distance = np.max(distances)

print(f"Mean distance from center: {mean_distance:.2f} m")
print(f"Max distance from center: {max_distance:.2f} m")


plt.figure()
plt.scatter(eastings, northings, s=10, label='GPS readings')
plt.scatter(mean_easting, mean_northing, color='red', marker='x', s=100, label='Mean position')
plt.xlabel('UTM Easting (m)')
plt.ylabel('UTM Northing (m)')
plt.title('Stationary GPS Data Scatter Plot')
plt.legend()
plt.axis('equal')
plt.savefig('stationary_scatter.png')
print("Saved plot to stationary_scatter.png")

times = np.array([float(row['sec']) for row in rows])
times = times - times[0]  

plt.figure()
sc = plt.scatter(eastings, northings, c=times, cmap='viridis', s=10)
plt.colorbar(sc, label='Time since start (s)')
plt.scatter(mean_easting, mean_northing, color='red', marker='x', s=100, label='Mean position')
plt.xlabel('UTM Easting (m)')
plt.ylabel('UTM Northing (m)')
plt.title('Stationary GPS Data — Colored by Time')
plt.legend()
plt.axis('equal')
plt.savefig('stationary_scatter_time.png')
print("Saved plot to stationary_scatter_time.png")
