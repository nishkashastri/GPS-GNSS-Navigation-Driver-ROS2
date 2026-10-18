from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    port = LaunchConfiguration('port')
    return LaunchDescription([
        DeclareLaunchArgument('port', default_value='/dev/ttyUSB0'),
        Node(
            package='imu_driver',
            executable='driver.py',
            name='imu_driver',
            parameters=[{'port': port}],
            output='screen',
        ),
    ])
