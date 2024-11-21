import rclpy

from rclpy.node import Node

from geometry_msgs.msg import Twist # data type of the cmd_vel topic message - 6 numbers - velocity and angular velocity in x,y,z

from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
# target frame - base_link
# source frame(parent) - odom

import json


import math 
def euler_from_quaternion(x, y, z, w):  # because ros uses this as orientation representation
        """
        Convert a quaternion into euler angles (roll, pitch, yaw)
        roll is rotation around x in radians (counterclockwise)
        pitch is rotation around y in radians (counterclockwise)
        yaw is rotation around z in radians (counterclockwise)
        """
        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + y * y)
        roll_x = math.atan2(t0, t1)
     
        t2 = +2.0 * (w * y - z * x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        pitch_y = math.asin(t2)
     
        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        yaw_z = math.atan2(t3, t4)
     
        return roll_x, pitch_y, yaw_z # in radians



class controlNode(Node):
        
    def __init__(self):
        
        super().__init__('direction_control')
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)   # a gazebo plugin is listening for commands on this toppic (libgazebo_ros_diff_drive.so)
        timer_period = 0.1  # seconds
        
        # Declare and acquire `target_frame` parameter
        self.target_frame = self.declare_parameter('target_frame', 'base_link').get_parameter_value().string_value  # self.target_frame is the CHILD
        self.wayJson = self.declare_parameter('path_to_json', '/home/martin/dev_ws/src/my_bot-main/launch/waypoints.json').get_parameter_value().string_value  # path to json waypoint list
        self.ANGLE_SENSITIVITY = float(self.declare_parameter('angle_sensitivity', 0.01).get_parameter_value().double_value)  # coefficient for regulation
        self.MINDIST = float(self.declare_parameter('min_dist', 0.1).get_parameter_value().double_value)    # in m, proximity to switch to next waypoint
        self.MAX_SPEED = float(self.declare_parameter('max_speed', 0.5).get_parameter_value().double_value) # m/s
        
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        
        with open(self.wayJson, "r") as file: loaded = json.load(file)
        
        self.waypoints = loaded["waypoints"]
        self.posX = self.waypoints[0][0]    # first waypoint is the initial robot position
        self.posY = self.waypoints[0][1]
        self.rotZ = loaded["yaw"]
        self.currentWP = 1
        #self.ANGLE_SENSITIVITY = 0.01    # coefficient for regulation
        
        self.timer = self.create_timer(timer_period, self.timer_callback)
        
    def timer_callback(self):
        
        childFrame = self.target_frame
        parentFrame = 'odom'
        
        msg = Twist()
        # these do not matter - the robot only has two wheels
        msg.linear.y = 0.0  # m/s
        msg.linear.z = 0.0
        msg.angular.x = 0.0   # rad/s
        msg.angular.y = 0.0
        try:
            # get robots current position
            tr = self.tf_buffer.lookup_transform(parentFrame, childFrame, rclpy.time.Time())
            self.posX = tr.transform.translation.x
            self.posY = tr.transform.translation.y
            self.rotZ = euler_from_quaternion(tr.transform.rotation.x, tr.transform.rotation.y, tr.transform.rotation.z, tr.transform.rotation.w)[2]
            #self.get_logger().info(str(self.posX) + " | " + str(self.posY) + " | " + str(self.rotZ))
            
            if(  math.dist(self.waypoints[self.currentWP], (self.posX, self.posY)) <= self.MINDIST ):   self.currentWP += 1
            if(self.currentWP >= len(self.waypoints)):   # no more waypoints - stop
                msg.linear.x = 0.0
                msg.angular.z = 0.0
                
            else:
                x = self.waypoints[self.currentWP][0]
                y = self.waypoints[self.currentWP][1]
                corrAngle = math.atan2(y-self.posY, x-self.posX)    # (y, x)
                msg.linear.x = self.MAX_SPEED
                diff = corrAngle - self.rotZ
                if diff > math.pi: diff -= 2*math.pi 
                if diff < -math.pi: diff += 2*math.pi 
                msg.angular.z = self.ANGLE_SENSITIVITY * diff    # positive is counter-clockwise
                self.get_logger().info("correct angle: " + str(corrAngle) + "   current angle: " + str(self.rotZ) + "   change: " + str(diff))
                         
        except Exception as e:
            #self.get_logger().info(str(e))
            #self.get_logger().info("Error reading transform - doing nothing")
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            
        self.publisher_.publish(msg)
        #self.get_logger().info("Publishing: linear = " + str(msg.linear) + " angular = " + str(msg.angular))
        
def main(args=None):
    rclpy.init(args=args)

    control = controlNode()

    rclpy.spin(control)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automaticallywhen the garbage collector destroys the node object)
    control.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()