import numpy as np
import matplotlib.pyplot as plt
from mcap_ros2.reader import read_ros2_messages

BAG = "car_drive/car_drive_0.mcap"

# IMU 
t, acc, gyr, mag, yaw = [], [], [], [], []
for m in read_ros2_messages(BAG, topics=["/imu"]):
    msg = m.ros_msg
    a = msg.imu.linear_acceleration
    g = msg.imu.angular_velocity
    b = msg.mag_field.magnetic_field
    t.append(m.log_time_ns * 1e-9)
    acc.append([a.x, a.y, a.z])
    gyr.append([g.x, g.y, g.z])
    mag.append([b.x * 1e4, b.y * 1e4, b.z * 1e4])     
    yaw.append(float(msg.raw_string.split(",")[1]))    

# GPS 
tg, east, north = [], [], []
for m in read_ros2_messages(BAG, topics=["/gps"]):
    tg.append(m.log_time_ns * 1e-9)
    east.append(m.ros_msg.utm_easting)
    north.append(m.ros_msg.utm_northing)

t, tg = np.array(t), np.array(tg)
t0 = t[0]
t, tg = t - t0, tg - t0                     
east = np.array(east) - east[0]             
north = np.array(north) - north[0]

np.savez("lab4_data.npz", t=t, acc=acc, gyr=gyr, mag=mag, yaw=yaw,
         tg=tg, east=east, north=north)
print("IMU samples:", len(t), " GPS samples:", len(tg), " duration:", t[-1], "s")

# Plots
fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))
ax[0].plot(t, np.array(gyr)[:, 2])
ax[0].set_xlabel("time (s)"); ax[0].set_ylabel("gyro z (rad/s)")
ax[0].set_title("Yaw rate"); ax[0].grid()
ax[1].plot(east, north)
ax[1].set_xlabel("East (m)"); ax[1].set_ylabel("North (m)")
ax[1].set_title("GPS track"); ax[1].axis("equal"); ax[1].grid()
plt.tight_layout(); plt.show()