import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from time import sleep
import sys
import tty
import termios
import select

def getch(timeout = 0.1):
    fd = sys.stdin.fileno()
    old_setting = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        rlist, _, _ = select.select([sys.stdin], [], [], timeout)
        if rlist:
            ch = sys.stdin.read(1)
            return ch
        else:
            return None
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_setting)

class keyboard_control_node(Node):
    def __init__(self):
        super().__init__('control_node')
        self.publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.linear_speed = 0.0
        self.angular_speed = 0.0

    def publish_cmd(self):
        twist = Twist()
        twist.linear.x = self.linear_speed
        twist.angular.z = self.angular_speed
        self.publisher.publish(twist)

    def run(self):
        if rclpy.ok():
            self.get_logger().info('Starting keyboard control. Press f to exit.')
        while rclpy.ok():
            key = getch()
            if key:
                if key == 'q':
                    self.linear_speed = 0.3
                    self.angular_speed = 0.3
                elif key == 'w':
                    self.linear_speed = 0.5
                    self.angular_speed = 0.0
                elif key == 'e':
                    self.linear_speed = 0.3
                    self.angular_speed = -0.3
                elif key == 'a':
                    self.linear_speed = 0.0
                    self.angular_speed = 0.5
                elif key == 's':
                    self.linear_speed = 0.0
                    self.angular_speed = 0.0
                elif key == 'd':
                    self.linear_speed = 0.0
                    self.angular_speed = -0.5
                elif key == 'z':
                    self.linear_speed = -0.3
                    self.angular_speed = -0.3
                elif key == 'x':
                    self.linear_speed = -0.5
                    self.angular_speed = 0.0
                elif key == 'c':
                    self.linear_speed = -0.3
                    self.angular_speed = 0.3
                elif key == 'f':
                    self.get_logger().info('Exiting...')
                    break
                else:
                    self.linear_speed = 0.0
                    self.angular_speed = 0.0
            else:
                self.linear_speed = 0.0
                self.angular_speed = 0.0

            self.publish_cmd()


def main(args=None):
    rclpy.init(args=args)
    node = keyboard_control_node()
    try:
        node.run()
    finally:
        node.destroy_node()
        rclpy.shutdown()