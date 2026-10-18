#!/usr/bin/env python3
import csv, math, sys
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message


def quat_to_euler(x, y, z, w):
    """Quaternion -> roll, pitch, yaw in degrees."""
    roll = math.atan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y))
    s = max(-1.0, min(1.0, 2 * (w * y - z * x)))
    pitch = math.asin(s)
    yaw = math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
    return math.degrees(roll), math.degrees(pitch), math.degrees(yaw)


bag, out = sys.argv[1], sys.argv[2]
reader = rosbag2_py.SequentialReader()
reader.open(rosbag2_py.StorageOptions(uri=bag, storage_id='mcap'),
            rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in reader.get_all_topics_and_types()}
msg_type = get_message(types['/imu'])

with open(out, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['time', 'roll_deg', 'pitch_deg', 'yaw_deg',
                'gyro_x', 'gyro_y', 'gyro_z',
                'accel_x', 'accel_y', 'accel_z',
                'mag_x', 'mag_y', 'mag_z'])
    t0 = None
    while reader.has_next():
        topic, data, _ = reader.read_next()
        if topic != '/imu':
            continue
        m = deserialize_message(data, msg_type)
        t = m.header.stamp.sec + m.header.stamp.nanosec * 1e-9
        t0 = t if t0 is None else t0
        q = m.imu.orientation
        r, p, y = quat_to_euler(q.x, q.y, q.z, q.w)
        g, a, mg = m.imu.angular_velocity, m.imu.linear_acceleration, m.mag_field.magnetic_field
        w.writerow([t - t0, r, p, y, g.x, g.y, g.z, a.x, a.y, a.z, mg.x, mg.y, mg.z])
print('Saved', out)
