import rclpy
from rclpy.node import Node
from time import sleep
from new_interface.action import MoveRobot
from rclpy.action import ActionClient

import math


class MoveDistanceClient(Node):
    def __init__(self):
        super().__init__('move_distance_action_server')

        self._action_client = ActionClient(
            self,
            MoveRobot,
            'move_distance'
        )

    def send_goal(self, move_x, move_y):
        goal_msg = MoveRobot.Goal()
        goal_msg.move_x = move_x
        goal_msg.move_y = move_y

        self._action_client.wait_for_server()

        future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback    
        )

        future.add_done_callback(self.goal_response_callback)

    def feedback_callback(self, feedback_msg):
        remained = feedback_msg.feedback.remained_distance
        self.get_logger().info(f"Remained: {remained:.2f} m")

    def goal_response_callback(self, feedback_msg):
        goal_handle = feedback_msg.result()

        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return

        self.get_logger().info('Goal accepted')

        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().result
        if result.success:
            self.get_logger().info('Goal succeeded!')
        else:
            self.get_logger().info('Goal failed!')

def main(args=None):
    rclpy.init(args=args)

    move_distance_client = MoveDistanceClient()

    import threading
    def input_thread():
        while True:
            move_x = float(input("请输入x轴移动的距离"))
            move_y = float(input("请输入y轴移动的距离"))

            try:
                move_distance_client.send_goal(move_x, move_y)
            except Exception as e:
                move_distance_client.get_logger().error(f"发送目标失败: {e}")

    thread = threading.Thread(target=input_thread, daemon=True)
    thread.start()

    rclpy.spin(move_distance_client)
    move_distance_client.destroy_node()
    rclpy.shutdown()