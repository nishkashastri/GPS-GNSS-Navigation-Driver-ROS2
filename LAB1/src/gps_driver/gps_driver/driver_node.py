import rclpy
from rclpy.node import Node
from gps_msgs.msg import GPSmsg
import serial

from gps_driver.gpgga_parser import parse_gpgga

class GPSDriverNode(Node):
    def __init__(self):
        super().__init__('gps_driver_node')
        self.get_logger().info('GPS driver node started')

        self.serial_conn = serial.Serial('/dev/ttyUSB0', 4800, timeout=3.0)
        self.timer = self.create_timer(0.2, self.read_and_parse)
        self.publisher_ = self.create_publisher(GPSmsg, 'gps', 10)

    def read_and_parse(self):
        latest_gpgga_line = None

        while self.serial_conn.in_waiting > 0:
            raw = self.serial_conn.readline()
            line = raw.decode('ascii', errors='replace').strip()

            if line.startswith('$GPGGA'):
                latest_gpgga_line = line

        if latest_gpgga_line is None:
            return  # no fresh GPGGA sentence available this tick

        result = parse_gpgga(latest_gpgga_line)

        if result is None:
            self.get_logger().warn('No fix yet')
            return

        self.get_logger().info(f"lat={result['latitude']}, lon={result['longitude']}")
        msg = GPSmsg()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'GPS1_Frame'
        msg.latitude = result['latitude']
        msg.longitude = result['longitude']
        msg.altitude = result['altitude']
        msg.utm_easting = result['utm_easting']
        msg.utm_northing = result['utm_northing']
        msg.zone = result['zone_number']
        msg.letter = result['zone_letter']

        self.publisher_.publish(msg)
def main(args=None):
    rclpy.init(args=args)
    node = GPSDriverNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

