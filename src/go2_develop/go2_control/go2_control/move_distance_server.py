import rclpy
from rclpy.node import Node
from time import sleep
from new_interface.action import MoveRobot
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
from rclpy.action import ActionServer
from rclpy.executors import MultiThreadedExecutor
from go2_control.utils import euler_from_quaternion
import math


class MoveDistanceServer(Node):
    def __init__(self):
        super().__init__('move_distance_action_server')

        self.cmd_vel_publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.odom_subscriber = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_subscriber_callback,
            10
        )
        self._action_server = ActionServer(
            self,
            MoveRobot,
            'move_distance',
            self.execute_callback
        )

        self.current_x = 0.0
        self.current_y = 0.0
        self.current_yam = 0.0

        self.get_logger().info('Move Distance Action Server has been started.')

    def odom_subscriber_callback(self, msg):
        # self.get_logger().info(f"Received odometry")
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y

        q = msg.pose.pose.orientation
        yaw = euler_from_quaternion(q)
        self.current_yam = yaw

    async def execute_callback(self, goal_handle):
        self.get_logger().info("Received goal request")

        target_x = goal_handle.request.move_x + self.current_x
        target_y = goal_handle.request.move_y + self.current_y

        self.get_logger().info(f"Target position: ({target_x:.2f}, {target_y:.2f})")

        feedback_msg = MoveRobot.Feedback()
        twist = Twist()

        max_linear_speed = 0.5
        min_linear_speed = 0.2
        speed_rate = 0.5
        max_angular_speed = 0.3
        angular_rate = 1.5


        pos_tolerance = 0.02
        angle_tolerance = 0.1

        while rclpy.ok():
            dx = target_x - self.current_x
            dy = target_y - self.current_y
            # self.get_logger().info(f"Current distance moved: {dx:.2f} m {dy:.2f} m")
            distance_remained = math.sqrt(dx*dx + dy*dy)

            target_yaw = math.atan2(dy, dx)
            yaw_error = target_yaw - self.current_yam
            yaw_error = math.atan2(math.sin(yaw_error), math.cos(yaw_error))

            feedback_msg.remained_distance = distance_remained
            goal_handle.publish_feedback(feedback_msg)


            if distance_remained < pos_tolerance:
                break
            
            if abs(yaw_error) > math.pi / 2:
                twist.linear.x = 0.0
                twist.angular.z = max_angular_speed if yaw_error > 0 else -max_angular_speed
            else:
                twist.linear.x = max(min_linear_speed, min(max_linear_speed, speed_rate * distance_remained))
                twist.angular.z = max(-max_angular_speed, min(max_angular_speed, angular_rate * yaw_error))

            self.cmd_vel_publisher.publish(twist)
            sleep(0.1)

        twist.linear.x = 0.0
        twist.angular.z = 0.0
        self.cmd_vel_publisher.publish(twist)

        goal_handle.succeed()
        result = MoveRobot.Result()
        result.success = True

        self.get_logger().info("Goal succeeded, target distance reached.")
        return result

def main(args=None):
    rclpy.init(args=args)

    move_distance_server = MoveDistanceServer()

    executor = MultiThreadedExecutor()
    executor.add_node(move_distance_server)
    try:
        executor.spin()
    finally:
        move_distance_server.destroy_node()
        rclpy.shutdown()