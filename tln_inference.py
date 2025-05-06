# Script to run TLN inference only, no object detection or turret functionality here

# Authors: Angelo DiTocco, Connor Meybohm, Julian Stala, Alan Weiss (ECD508)
# Converted from a script by: Mohammed Misbah Zarrar, Qitao Weng, Bakhbyergyen Yerjan, Ahmet Soyyigit, Heechul Yun (CSL-KU)

# Imports for TLN inference
import time
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.clock import Clock
from builtin_interfaces.msg import Time
import tensorflow as tf
from sensor_msgs.msg import LaserScan
from sensor_msgs.msg import Joy
from ackermann_msgs.msg import AckermannDriveStamped
from std_msgs.msg import Float64
from nav_msgs.msg import Odometry
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.executors import MultiThreadedExecutor
import threading

# TLN model name
tln_model_name = './TLN/Models/TLN_12_environments_galore_noquantized.tflite'

# ROS 2 topics
lidar_filtered_topic = '/scan_filtered'
lidar_topic = '/scan'
odom_topic = "/odom"
rpm_topic = '/commands/motor/speed'
drive_topic = '/drive' 

# Main function
def main(args=None):

	# Set up ROS 2 publisher and subscriber nodes
	rclpy.init(args=args)

	drivePublisher = DrivePublisher(drive_topic)
	rpmSubscriber = RPMSubscriber(rpm_topic)
	odometrySubscriber = OdometrySubscriber(odom_topic)
	lidarSubscriber = LidarSubscriber(lidar_filtered_topic, subsample_lidar=2)
	#joySubscriber = JoySubscriber()

	#Create a multi-threaded executor to run all nodes at once
	executor = MultiThreadedExecutor()
	executor.add_node(drivePublisher)
	executor.add_node(rpmSubscriber)
	executor.add_node(odometrySubscriber)
	executor.add_node(lidarSubscriber)
	#executor.add_node(joySubscriber)
	thread = threading.Thread(target=executor.spin, daemon=True)
	thread.start()
	
	# Load TLN Model
	model_data = load_tln()

	# Main loop
	i = 0
	while(i == 0):

		# Set up a drive message to publish speed and steering
		clock = Clock()
		msg = AckermannDriveStamped()
		currentTime = clock.now()
		msg.header.stamp = currentTime.to_msg()
		msg.header.frame_id = "base_link"
		
		# Use TLN to get servo and speed
		lidar_data = lidarSubscriber.getLidarData()
		servo, speed = tln_inference(lidar_data, model_data)

		# Print throttle and sterring data if needed for debugging
		# print(f'Servo: {servo}, Speed: {speed}')

		# Publish the speed and servo messages
		msg.drive.speed = float(speed)
		msg.drive.steering_angle = float(servo)
		drivePublisher.drive_pub.publish(msg)
	
	# Clean up nodes once done
	# Not sure if this ever actually happens because we're just using Ctrl-C to kill the program
	drivePublisher.destroy_node()
	rpmSubscriber.destroy_node()
	odometrySubscriber.destroy_node()
	lidarSubscriber.destroy_node()
	#joySubscriber.destroy_node()
	rclpy.shutdown()

# Load the TensorFlow Lite model
def load_tln():
	print(f"Loading TLN model: {tln_model_name}")
	interpreter = tf.lite.Interpreter(model_path=tln_model_name)
	interpreter.allocate_tensors()
	input_index = interpreter.get_input_details()[0]["index"]
	output_details = interpreter.get_output_details()

	# Save data to a dictionary for cleaner access
	model_data = {
		"interpreter": interpreter,
		"input_index": input_index,
		"output_details": output_details
	}

	return model_data

# Run the LiDAR data through the model to get speed and steering predictions
def tln_inference(lidar_data, model_data):
	if lidar_data is None:
		return 0.0, 0.0
    
	# Extract model data from the dictionary
	interpreter = model_data["interpreter"]
	input_index = model_data["input_index"]
	output_details = model_data["output_details"]

	interpreter.set_tensor(input_index, lidar_data)
	start_time = time.time()
	interpreter.invoke()

	# Get inference time if needed for debugging
	# inf_time = (time.time() - start_time) * 1000 
	# print("Inference Time: {inf_fime}")

	output = interpreter.get_tensor(output_details[0]['index'])
    
	servo = output[0, 0]  # Extract predicted servo angle
	speed = output[0, 1]  # Extract predicted speed
	
	# Run linear map on speed
	speed = linear_map(speed, 0, 1, -0.5, 7.0)

	return servo, speed

# Linear mapping function
def linear_map(x, x_min, x_max, y_min, y_max):
    return (x - x_min) / (x_max - x_min) * (y_max - y_min) + y_min

# Node to publish to drive topic
class DrivePublisher(Node):
	def __init__(self, drive):
		super().__init__('drive_publisher')
		drive_cb_group = MutuallyExclusiveCallbackGroup() 
		self.drive_pub = self.create_publisher(
			AckermannDriveStamped, 
			drive_topic, 
			10,
			callback_group = drive_cb_group
		)
		
	def driveCallback(self, msg):
		self.drive_pub.publish(msg)

# Node to subscribe to RPM topic
class RPMSubscriber(Node):
	def __init__(self, rpm_topic):
		super().__init__('rpm_subscriber')
		self.wheel_speed = 0
		rpm_cb_group = MutuallyExclusiveCallbackGroup() 
		self.subscription = self.create_subscription(
			Float64,
			rpm_topic,
			self.rpmCallback,
			10,
			callback_group = rpm_cb_group 
		)
		
	def rpmCallback(self, msg):
		self.wheel_speed = msg
		#self.get_logger().info(f'RPM: {msg}')
		
# VESC Odometry subscriber
class OdometrySubscriber(Node):
	def __init__(self, odom_topic):
		super().__init__('odometry_subscriber')
		self.start_position = None
		self.total_distance = 0.0
		odom_cb_group = MutuallyExclusiveCallbackGroup() 
		self.subscription = self.create_subscription(
			Odometry,
			odom_topic,
			self.odometryCallback,
			10,
			callback_group = odom_cb_group 
		)
		
	def odometryCallback(self, msg):
		if self.start_position is None:
			self.start_position = [msg.pose.pose.position.x, msg.pose.pose.position.y]
			return
		current_position = [msg.pose.pose.position.x, msg.pose.pose.position.y]
		distance = np.linalg.norm(np.array(current_position) - np.array(self.start_position))
		self.total_distance += distance
		self.start_position = current_position

		# Print odometry data if needed for debugging
		#self.get_logger().info(f'Odometry received: {msg}')

# Node to subscribe to LiDAR topic
class LidarSubscriber(Node):
	def __init__(self, lidar_filtered_topic, subsample_lidar):
		super().__init__('lidar_subscriber')
		self.lidar_data = None
		lidar_cb_group = MutuallyExclusiveCallbackGroup() 
		self.subsample_lidar = subsample_lidar
		self.subscription = self.create_subscription(
			LaserScan,
			lidar_filtered_topic,
			self.lidarCallback,
			10,
			callback_group = lidar_cb_group 
		)
		
	def lidarCallback(self, msg):
		ldata = msg.ranges[::self.subsample_lidar]  
		ldata = np.expand_dims(ldata, axis=-1).astype(np.float32)  # Reshape and convert to float32
		ldata = np.expand_dims(ldata, axis=0)  # Add batch dimension
		self.lidar_data = ldata  # Store the processed Lidar data

		# Print LiDAR data if needed for debugging
		#self.get_logger().info(f'Ranges: {msg.ranges}, Intensities: {msg.intensities}')
		
	def getLidarData(self):
		return self.lidar_data

# Joystick subscriber in case we need to process controller input
class JoySubscriber(Node):
	def __init__(self):
		super().__init__('joy_subscriber')
		joy_cb_group = MutuallyExclusiveCallbackGroup()
		self.subscription = self.create_subscription(
			Joy,
			'joy',
			self.joyCallback,
			10,
			callback_group = joy_cb_group
		)
		self.subscription
		
	def joyCallback(self, msg):

		# Process button input here
		# To see which buttons get which numbers, run jstest /dev/input/joypad-f710

		# self.get_logger().info(f'Axes: {msg.axes}, Buttons: {msg.buttons}')

		pass

# Undo min-max scaling (we don't seem to need this right now)
# def undo_min_max_scale(x, x_min, x_max):
#     return x * (x_max - x_min) + x_min

if __name__ == '__main__':
	main()
