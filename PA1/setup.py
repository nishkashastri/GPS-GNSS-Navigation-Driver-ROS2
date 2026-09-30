from setuptools import find_packages, setup

package_name = 'pa1_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='root',
    maintainer_email='root@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
		'talker = pa1_pkg.publisher_node:main',
		'listener = pa1_pkg.subscriber_node:main',
		'add_two_ints_server = pa1_pkg.service_server_node:main',
            	'add_two_ints_client = pa1_pkg.service_client_node:main',
        ],
    },
)
