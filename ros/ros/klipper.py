# import klipper and run from script
# Node definition should be
import sys, gc, time, os

import rclpy.time

klippy_path = "/home/arvaipeter/projects/OE/MSC/ros_ws/src/SMFirmware/klippy"

if not os.path.exists(klippy_path):
    print("Could not find klipper modules")
    exit()

sys.path.append(klippy_path)

import rclpy.node
import util, queuelogger
import rclpy

from klippy import Printer
from reactor import Reactor

from sensor_msgs.msg import JointState

class KlipperNode(rclpy.node.Node):
    
    def __init__(self):
        super().__init__("KlipperNode")

        self.position_publisher = self.create_publisher(
            JointState,
            "/joint_states",
            10
        )

    def publish_position(self, position):
        update_msg = JointState()
        update_msg.header.stamp = self.get_clock().now().to_msg()
        axes = ["x_axis_joint", "y_axis_joint", "z_axis_joint"]

        for i, axis in enumerate(axes):
            update_msg.position.append(position[i] / 1000) # mm to m
            update_msg.name.append(axis)
            
        self.position_publisher.publish(update_msg)
        rclpy.spin_once(self, timeout_sec=0)


def main(args=None):
    # Start ros
    rclpy.init(args=args)
    klipper_ros = KlipperNode()

    # Klipper config
    
    start_args = {
        "config_file": "/home/arvaipeter/projects/OE/MSC/printer_data/config/printer.cfg",
        "log_file": "/home/arvaipeter/projects/OE/MSC/printer_data/logs/klippy.log",
        "apiserver": "/home/arvaipeter/projects/OE/MSC/printer_data/comms/klippy.sock",
        "start_reason": "startup",
        "gcode_fd": util.create_pty("/home/arvaipeter/projects/OE/MSC/printer_data/comms/klippy.serial"),
        "cpu_info": util.get_cpu_info(),
        "ROS": klipper_ros 
    }
    bglogger = queuelogger.setup_bg_logging(start_args["log_file"], 20) # 20 = logging.info 
    gc.disable()

    # Run klipper
    gc.collect()

    main_reactor = Reactor(gc_checking=True)
    printer = Printer(main_reactor, bglogger, start_args)

    printer.run()

    time.sleep(1.)
    main_reactor.finalize()
    main_reactor = print = None

    klipper_ros.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()