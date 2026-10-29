import numpy as np
import matplotlib.pyplot as plt
from mcap_ros2.reader import read_ros2_messages

BAG = "car_drive/car_drive_0.mcap"
T_CIRCLES = (25, 88)        # car driving in circles
T_ROUTE = 88.0              # route starts where the circles end

t, acc, gyr, mag, yaw, pitch, roll = [], [], [], [], [], [], []
for m in read_ros2_messages(BAG, topics=["/imu"]):
    msg = m.ros_msg
    a = msg.imu.linear_acceleration
    g = msg.imu.angular_velocity
    b = msg.mag_field.magnetic_field
    f = msg.raw_string.split(",")
    t.append(m.log_time_ns * 1e-9)
    acc.append([a.x, a.y, a.z])
    gyr.append([g.x, g.y, g.z])
    mag.append([b.x * 1e4, b.y * 1e4, b.z * 1e4])    
    yaw.append(float(f[1]))                          
    pitch.append(float(f[2]))                        
    roll.append(float(f[3]))                         

tg, east, north = [], [], []
for m in read_ros2_messages(BAG, topics=["/gps"]):
    tg.append(m.log_time_ns * 1e-9)
    east.append(m.ros_msg.utm_easting)
    north.append(m.ros_msg.utm_northing)

t, acc, gyr, mag = np.array(t), np.array(acc), np.array(gyr), np.array(mag)
yaw, pitch, roll = np.array(yaw), np.array(pitch), np.array(roll)
tg, east, north = np.array(tg), np.array(east), np.array(north)
t0 = t[0]
t, tg = t - t0, tg - t0

# Circles
c = (t >= T_CIRCLES[0]) & (t <= T_CIRCLES[1])
np.savez("circles.npz", t=t[c] - t[c][0], acc=acc[c], gyr=gyr[c],
         mag=mag[c], pitch=pitch[c], roll=roll[c])

# Route 
r = t >= T_ROUTE
g = tg >= T_ROUTE
E0 = np.interp(T_ROUTE, tg, east) 
N0 = np.interp(T_ROUTE, tg, north)
np.savez("route.npz",
         t=t[r] - T_ROUTE, acc=acc[r], gyr=gyr[r], mag=mag[r],
         yaw=yaw[r], pitch=pitch[r], roll=roll[r],
         tg=tg[g] - T_ROUTE, east=east[g] - E0, north=north[g] - N0)

print("Circles: IMU samples", c.sum())
print("Route:   IMU samples", r.sum(), " GPS samples", g.sum(),
      " duration", round(t[r][-1] - T_ROUTE, 1), "s")

# Plots 
fig, ax = plt.subplots(1, 3, figsize=(15, 4.5))
ax[0].plot(t, gyr[:, 2], lw=0.5, color="gray")
ax[0].axvspan(*T_CIRCLES, color="tab:orange", alpha=0.3, label="circles.npz")
ax[0].axvspan(T_ROUTE, t[-1], color="tab:blue", alpha=0.15, label="route.npz")
ax[0].set_xlabel("time (s)"); ax[0].set_ylabel("gyro z (rad/s)")
ax[0].set_title("Full drive and the two parts"); ax[0].legend(); ax[0].grid()
ax[1].plot(mag[c, 0], mag[c, 1], ".", ms=2)
ax[1].set_xlabel("Mag X (G)"); ax[1].set_ylabel("Mag Y (G)")
ax[1].set_title("circles.npz: mag X vs Y"); ax[1].axis("equal"); ax[1].grid()
ax[2].plot(east[g] - E0, north[g] - N0, "k")
ax[2].plot(0, 0, "go", ms=8, label="Route start (end of circles)")
ax[2].set_xlabel("East (m)"); ax[2].set_ylabel("North (m)")
ax[2].set_title("route.npz: GPS track"); ax[2].axis("equal"); ax[2].grid()
ax[2].legend()
plt.tight_layout(); plt.show()