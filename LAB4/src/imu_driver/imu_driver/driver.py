import math
import time
import serial
import rclpy
from rclpy.node import Node
from imu_driver.msg import IMUmsg


def nmea_checksum(body):
    """XOR of all characters between '$' and '*'."""
    cs = 0
    for c in body:
        cs ^= ord(c)
    return cs


def make_command(body):
    return f"${body}*{nmea_checksum(body):02X}\r\n".encode()


def checksum_ok(line):
    if not line.startswith('$') or '*' not in line:
        return False
    body, cs = line[1:].split('*', 1)
    try:
        return nmea_checksum(body) == int(cs[:2], 16)
    except ValueError:
        return False


def euler_to_quaternion(roll, pitch, yaw):
    """ZYX (yaw-pitch-roll) Euler angles in radians -> (x, y, z, w)."""
    cr, sr = math.cos(roll / 2), math.sin(roll / 2)
    cp, sp = math.cos(pitch / 2), math.sin(pitch / 2)
    cy, sy = math.cos(yaw / 2), math.sin(yaw / 2)
    w = cr * cp * cy + sr * sp * sy
    x = sr * cp * cy - cr * sp * sy
    y = cr * sp * cy + sr * cp * sy
    z = cr * cp * sy - sr * sp * cy
    return x, y, z, w


class IMUDriver(Node):
    def __init__(self):
        super().__init__('imu_driver')
        self.declare_parameter('port', '/dev/ttyUSB0')
        self.declare_parameter('baudrate', 115200)
        port = self.get_parameter('port').value
        baud = self.get_parameter('baudrate').value

        self.ser = serial.Serial(port, baud, timeout=1.0)
        self.get_logger().info(f'Opened {port} at {baud} baud')
        self.configure_imu()
        self.pub = self.create_publisher(IMUmsg, 'imu', 10)

    def configure_imu(self):
        
        for body in ('VNWRG,06,14', 'VNWRG,07,40'):
            self.ser.write(make_command(body))
            self.ser.flush()
            time.sleep(0.1)
        self.ser.reset_input_buffer()
        self.get_logger().info('IMU set to VNYMR @ 40 Hz')

    def read_and_publish(self):
        raw = self.ser.readline().decode('ascii', errors='ignore').strip()
        idx = raw.find('$VNYMR')
        if idx < 0:
            return
        line = raw[idx:]
        if not checksum_ok(line):
            self.get_logger().warn(f'Bad checksum: {line}')
            return

        fields = line[1:].split('*')[0].split(',')
        if len(fields) != 13:
            return
        try:
            yaw, pitch, roll, mx, my, mz, ax, ay, az, gx, gy, gz = map(float, fields[1:])
        except ValueError:
            return

        stamp = self.get_clock().now().to_msg()
        msg = IMUmsg()
        msg.header.stamp = stamp
        msg.header.frame_id = 'IMU1_Frame'
        msg.raw_imu = line

        qx, qy, qz, qw = euler_to_quaternion(
            math.radians(roll), math.radians(pitch), math.radians(yaw))
        msg.imu.header = msg.header
        msg.imu.orientation.x = qx
        msg.imu.orientation.y = qy
        msg.imu.orientation.z = qz
        msg.imu.orientation.w = qw

        msg.imu.angular_velocity.x = gx
        msg.imu.angular_velocity.y = gy
        msg.imu.angular_velocity.z = gz
        msg.imu.linear_acceleration.x = ax
        msg.imu.linear_acceleration.y = ay
        msg.imu.linear_acceleration.z = az

        msg.mag_field.header = msg.header
        msg.mag_field.magnetic_field.x = mx * 1e-4
        msg.mag_field.magnetic_field.y = my * 1e-4
        msg.mag_field.magnetic_field.z = mz * 1e-4

        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = IMUDriver()
    try:
        while rclpy.ok():
            node.read_and_publish()
    except KeyboardInterrupt:
        pass
    finally:
        node.ser.close()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
