from mcap_ros2.reader import read_ros2_messages

BAG = "car_drive/car_drive_0.mcap"

for m in read_ros2_messages(BAG, topics=["/imu"]):
    print(m.ros_msg)
    break

for m in read_ros2_messages(BAG, topics=["/gps"]):
    print(m.ros_msg)
    break