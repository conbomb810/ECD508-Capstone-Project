# Script to collect LiDAR & throttle/steering data in ROS 2 bags for training

# Authors: Angelo DiTocco, Connor Meybohm, Julian Stala, Alan Weiss (ECD508)
# Converted from a script by: Mohammed Misbah Zarrar, Qitao Weng, Bakhbyergyen Yerjan, Ahmet Soyyigit, Heechul Yun (CSL-KU)

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import Joy, LaserScan
from ackermann_msgs.msg import AckermannDriveStamped
import rosbag2_py
from collections import deque
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.executors import MultiThreadedExecutor
import threading
from pathlib import Path
import shutil
from rclpy.serialization import serialize_message
from rclpy import time
import time
from message_filters import ApproximateTimeSynchronizer, Subscriber
import sys

# ZIP timestamp issue hotfix
# Force set the date to something recent
#os.system("timedatectl set-time 2025-04-01")

# Define topics
drive_topic = '/teleop'
joy_topic = '/joy'
lidar_topic = '/scan_filtered'

bag_path = Path('./TLN/Dataset/out.db3')
bag_count = 0

qos_profile = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)

# Writer that will write to ROS bag
writer = None

class DataCollector(Node):
    def __init__(self):
        super().__init__('receive_position')

        # Subscribers
        self.drive_sub = Subscriber(
            self, 
            AckermannDriveStamped, 
            drive_topic, 
            qos_profile=qos_profile
        )
        self.lid_sub = Subscriber(
            self, 
            LaserScan, 
            lidar_topic, 
            qos_profile=qos_profile
        )

        # Time synchronizer
        self.ts = ApproximateTimeSynchronizer([self.drive_sub, self.lid_sub], queue_size=10, slop=0.01)
        self.ts.registerCallback(self.callback)
    
    def callback(self, ack_msg, ldr_msg):
        if writer:
            timestamp = self.get_clock().now().nanoseconds
            writer.write(drive_topic, serialize_message(ack_msg), timestamp)
            print("wrote ackermann message")
            writer.write(lidar_topic, serialize_message(ldr_msg), timestamp)
            print("wrote lidar message")


# Joystick subscriber
class JoySubscriber(Node):
    def __init__(self):
        super().__init__('joy_subscriber')
        joy_cb_group = MutuallyExclusiveCallbackGroup()
        self.subscription = self.create_subscription(
            Joy,
            joy_topic,
            self.joyCallback,
            10,
            callback_group=joy_cb_group
        )
        self.subscription

        # State for whether it is currently recording
        self.recording = False      

        # B button state to determine press (like a pulser)
        self.b_state = 0
        self.b_prev_state = 0

    def joyCallback(self, joy_msg):
        
        # Take the previous and current states of the B button
        self.b_prev_state = self.b_state
        self.b_state = joy_msg.buttons[1]#axes[5]

        # If the B button just got pressed, either stop or start recording
        if self.b_state and not self.b_prev_state:
            if not self.recording:
                stop_recording()
                self.recording = True
            else:
                start_recording()
                self.recording = False

        # self.get_logger().info(f"received button info: {joy_msg}")


def start_recording():
    #define the bag name and increment bag count for multiple recordings
    global bag_count 
    bag_count = bag_count + 1
    if (len(sys.argv) > 1):
        bag_path = Path('./TLN/Dataset/' + sys.argv[1] + "/" + str(bag_count))
    else:
        bag_path = Path('./TLN/Dataset/out' + "/" + str(bag_count))
    # don't make the recording if the bag path already exists
    if bag_path.exists():
        #shutil.rmtree(bag_path)
        print("existing bag found, please enter a different bag name")
        exit(0)

    # Initialize rosbag2 writer
    global writer
    storage_options = rosbag2_py.StorageOptions(uri=str(bag_path), storage_id='sqlite3')
    converter_options = rosbag2_py.ConverterOptions('', '')

    writer = rosbag2_py.SequentialWriter()
    writer.open(storage_options, converter_options)

    # Register message topics
    writer.create_topic(
        rosbag2_py.TopicMetadata(
            name=drive_topic,
            type='ackermann_msgs/msg/AckermannDriveStamped',
            serialization_format='cdr'
        )
    )
    writer.create_topic(
        rosbag2_py.TopicMetadata(
            name=lidar_topic,
            type='sensor_msgs/msg/LaserScan',
            serialization_format='cdr'
        )
    )


    print("Recording Started")


def stop_recording():
    # Close the rosbag2 writer
    global writer
    if writer:
        writer = None 
        print("Recording Stopped")


def main(args=None):

    rclpy.init(args=args)
    
    dataCollector = DataCollector()
    joySubscriber = JoySubscriber()

    # Create a multi-threaded executor
    executor = MultiThreadedExecutor()
    executor.add_node(dataCollector)
    executor.add_node(joySubscriber)
    
    # Run the executor in a separate thread
    thread = threading.Thread(target=executor.spin, daemon=True)
    thread.start()

    print("Beginning Program...")
    while True:
        pass
    
    dataCollector.destroy_node()
    joySubscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
