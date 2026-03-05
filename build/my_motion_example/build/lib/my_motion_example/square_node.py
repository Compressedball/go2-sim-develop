import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from time import sleep

class MoveNode(Node):
    def __init__(self):
        super().__init__('move_node')
        self.publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.timer = self.create_timer(1.0, self.move_square)
    
    def move_square(self):
        twist = Twist()
        # Move forward
        twist.linear.x = 0.5
        self.publisher.publish(twist)
        self.get_logger().info('Moving forward')
        sleep(2)  # Move for 2 seconds

        # Stop
        twist.linear.x = 0.0
        self.publisher.publish(twist)
        self.get_logger().info('Stopping')
        sleep(1)

        # Turn right
        twist.angular.z = -0.5
        self.publisher.publish(twist)
        self.get_logger().info('Turning right')
        sleep(2)  # Turn for 1 second

        # Stop
        twist.angular.z = 0.0
        self.publisher.publish(twist)
        self.get_logger().info('Stopping')
        sleep(1)


def main(args=None):
    rclpy.init(args=args)
    node = MoveNode()
    rclpy.spin(node)
    rclpy.shutdown()