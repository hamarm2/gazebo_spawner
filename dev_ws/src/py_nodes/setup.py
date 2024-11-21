from setuptools import setup

package_name = 'py_nodes'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='martin',
    maintainer_email='martin@todo.todo',
    description='Python nodes for 2-wheel vehicle control',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'controller = py_nodes.control_node:main'   # name for ros2 run, package name, node name, function, that will be called
        ],
    },
)
