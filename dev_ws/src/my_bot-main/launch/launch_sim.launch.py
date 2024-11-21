import os

from ament_index_python.packages import get_package_share_directory


from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node




def generate_launch_description():

    # Include the robot_state_publisher launch file, provided by our own package. Force sim time to be enabled
    # !!! MAKE SURE YOU SET THE PACKAGE NAME CORRECTLY !!!

    package_name='my_bot'

    with open("/home/martin/dev_ws/src/my_bot-main/launch/initPos.txt", "r") as file:
        initPos = file.readline().split()

    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','rsp.launch.py'
                )]), launch_arguments={'use_sim_time': 'true'}.items()
    )

    # Include the Gazebo launch file, provided by the gazebo_ros package
    gazebo = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')]),
             )


    # Run the spawner node from the gazebo_ros package. The entity name doesn't really matter if you only have a single robot.
    spawn_entity = Node(package='gazebo_ros', executable='spawn_entity.py',
                        arguments=['-topic', 'robot_description',
                                   '-entity', 'my_bot',  # my_bot is just a name
                                    '-x', initPos[0], '-y', initPos[1], '-z', initPos[2], '-Y', initPos[3]],  # init position
                                    
                        output='screen')

    # Start the control node
    params = {'use_sim_time': 'true',
              'target_frame': 'base_link',
              'path_to_json': '/home/martin/dev_ws/src/my_bot-main/launch/waypoints.json',
              'angle_sensitivity': 3.0,
              'min_dist': 0.1,
              'max_speed': 1.0
              }
    controller = Node(
        package='py_nodes',
        executable='controller',
        output='screen',
        parameters=[params]
    )

    # Launch them all!
    return LaunchDescription([
        rsp,
        gazebo,
        spawn_entity,
        controller,
    ])
