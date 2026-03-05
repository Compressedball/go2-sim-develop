import rclpy
from rclpy.node import Node
from time import sleep
from new_interface.action import MoveRobot
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
from rclpy.action import ActionServer
from rclpy.executors import MultiThreadedExecutor
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

        self.get_logger().info('Move Distance Action Server has been started.')

    def odom_subscriber_callback(self, msg):
        self.get_logger().info(f"Received odometry")
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y

    async def execute_callback(self, goal_handle):
        self.get_logger().info("Received goal request")
        target_distance = goal_handle.request.distance

        start_x = self.current_x
        start_y = self.current_y

        feedback_msg = MoveRobot.Feedback()
        twist = Twist()

        speed = 0.5
        tolerance = 0.02

        while rclpy.ok():
            dx = self.current_x - start_x
            dy = self.current_y - start_y
            self.get_logger().info(f"Current distance moved: {dx:.2f} m {dy:.2f} m")
            distance_moved = math.sqrt(dx*dx + dy*dy)

            feedback_msg.current_distance = distance_moved
            goal_handle.publish_feedback(feedback_msg)


            if distance_moved >= target_distance - tolerance:
                break

            twist.linear.x = speed
            self.cmd_vel_publisher.publish(twist)
            sleep(0.1)

        twist.linear.x = 0.0
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