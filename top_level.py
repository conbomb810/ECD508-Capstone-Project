# This is the Top Level FSM that drives the car and does all the functionalities
# Getting it modularized into multiple files would probably be ideal, but it's probably easiest to just have one file (at least for now)
# Authors: Angelo DiTocco, Connor Meybohm, Julian Stala, Alan Weiss (ECD508)

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

# Imports for YOLO
import cv2
from ultralytics import YOLO

# Imports for turret
import board
import busio
import adafruit_pca9685
from adafruit_servokit import ServoKit
import adafruit_motor.servo
import math

# FSM states
# A: drive autonomously with TLN
# B: stop at object
# C: identify object
# D: shoot at target
# E: drive past object
state = 'A'

# Specify model paths
tln_model_name = './TLN/Models/TLN_12_environments_galore_noquantized.tflite'
yolo_model_name = './YOLO/Models/custom_model_6.engine'

# Distance to stop from objects in inches
stop_dist = 72

# RealSense camera path
rs_path = '/dev/video4'

# Set width and height of camera feed to be used in object detection
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

# ROS 2 topics
lidar_filtered_topic = '/scan_filtered'
lidar_topic = '/scan'
odom_topic = "/odom"
rpm_topic = '/commands/motor/speed'
drive_topic = '/drive' 

# ServoKit setup
kit = ServoKit(channels=16)
i2c = busio.I2C(board.SCL, board.SDA)
pca = adafruit_pca9685.PCA9685(i2c)
pca.frequency = 60
# Define PWM channels for servos and laser diode
pan_servo = adafruit_motor.servo.Servo(pca.channels[0]) 
tilt_servo = adafruit_motor.servo.Servo(pca.channels[1])
laser_channel = pca.channels[3]
# Set rotation limits for servos
pan_servo.set_pulse_width_range(500, 2500)
tilt_servo.set_pulse_width_range(500, 2500)

# Servo values found through testing and RealSense specs
pitch_FORWARD = 35
pitch_MIN = 0
pitch_UP = 140
pitch_MAX = 58

yaw_CENTER = 92
yaw_MIN = 48
yaw_MAX = 136

# constant offsets from camera to turret
x_star = 0.375
y_star = 2.25 # Was 4.1875, then "we" (Alan) printed yet another mount # was 3.1875, then julian broke the turret # was 4.1875 then we printed a new mount
z_star = 4.75

# diameter of target in inches
d = 7.125

# constants from line of best fit
k = 865.634
c = 850.381

# Variable used as a start time for timing functions
ts = 0

# flag for target detection
target_detected = False

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
    
    # Take the RealSense webcam
    cap = cv2.VideoCapture(rs_path)

    # Set the resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

    # Set the exposure to minimize motion blur
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
    cap.set(cv2.CAP_PROP_EXPOSURE, 260)
    
    # Load models
    tln_model_data = load_tln()
    print(f"TLN model loaded: {tln_model_name}")
    yolo_model = YOLO(yolo_model_name, task="detect")
    print(f"YOLO model loaded: {yolo_model_name}")

    # Warm up the YOLO model to bypass first detection lag
    warmup_frame = cv2.imread("do_not_remove.jpg")
    yolo_model(warmup_frame, verbose=False)
    print("YOLO model warmed up")
        
    print(f"Stopping distance: {stop_dist} inches")

    # Reset servos
    pan_servo.angle = yaw_CENTER
    tilt_servo.angle = pitch_FORWARD

    # Main loop
    i = 0
    while(i == 0):

        global state
        global target_detected

        # Set up a drive message to publish speed and steering
        clock = Clock()
        msg = AckermannDriveStamped()
        currentTime = clock.now()
        msg.header.stamp = currentTime.to_msg()
        msg.header.frame_id = "base_link"

        # Get detections from YOLO model
        detections = get_detections(yolo_model, cap, False)
        target = find_object(detections, "target")
        stop_sign = find_object(detections, "stop_sign")
        
        # Main FSM
        if state == 'A':
            # Use TLN to get servo and speed
            lidar_data = lidarSubscriber.getLidarData()
            servo, speed = tln_inference(lidar_data, tln_model_data)

            # If an object is close enough (5 ft here), go to state B
            if object_within_distance(detections, stop_dist):
                state = 'B'
                print("switched to state B")
                reset_timer()

        elif state == 'B':

            # Straighten out steering and stop the car
            servo, speed = 0, 0

            # If the detected object is a target, keep tracking its position
            if target:
                X = target["x"]
                Y = target["y"]
                H = target["h"]
                target_detected = True

            # if it's been two seconds, go to state C
            if get_timer() > 2:
                state = 'C'
                print("switched to state C")

        elif state == 'C':
            # If the detected object is a target, go to state D
            if target_detected:
                state = 'D'
                print("switched to state D")
            else:
                print("switched to state E")
                state = 'E'

        elif state == 'D':

            # Aim at the target
            aim(X, Y, H)
            time.sleep(0.5)

            # Turn the laser pointer on and off
            laser_channel.duty_cycle = 0xFFFF
            time.sleep(1)
            laser_channel.duty_cycle = 0x0000
            
            # Reset servos back to original position
            pan_servo.angle = yaw_CENTER
            tilt_servo.angle = pitch_FORWARD
            time.sleep(0.5)

            # Go to state E
            print("switched to state E")
            state = 'E'

            # Start the timer for state E
            reset_timer()

            pass

        elif state == 'E':
            # Use TLN to get servo and speed
            lidar_data = lidarSubscriber.getLidarData()
            servo, speed = tln_inference(lidar_data, tln_model_data)

            # Stay in this state until an object is no longer close by for 2 seconds
            if object_within_distance(detections, stop_dist):
                reset_timer()
            elif get_timer() > 0.5:
                print("switched to state A")
                state = 'A'

            # Reset the target detected flag
            target_detected = False

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

def reset_timer():
    global ts
    ts = time.time()

def get_timer():
    global ts
    return time.time() - ts


# Load the TensorFlow Lite model
def load_tln():
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

# Function to run YOLO inference and return a list of any detected objects
def get_detections(model, cap, show_camera=True):

    # Make an empty list to store detections (dictionaries)
    detections = []

    # Read a frame from the video
    success, frame = cap.read()

    if success:
    
        # Run YOLO object detection on the frame
        results = model(frame, verbose=False, conf=0.5)

        # Get the detected object's box data
        boxes = results[0].boxes

        # If any objects detected...
        if len(boxes) > 0:

            # For each object:
            for box in boxes:

                # Get the number corresponding to the object class
                # 0 = stop sign
                # 1 = target
                class_id = int(boxes.cls[0].item())
                # Use the result's "name" dictionary to get the name of the object
                class_name = results[0].names[class_id]

                # Get the center x and y coords of the object
                # (xywh is a 2D tensor, so must index twice)
                x = int(boxes.xywh[0][0].item())
                y = int(boxes.xywh[0][1].item())
                h = int(boxes.xywh[0][3].item())

                # Get the inference time in ms
                inference_time = int(results[0].speed['inference'])

                # Put all that stuff in a dictionary
                detection = {}
                detection["name"] = class_name
                detection["x"] = x
                detection["y"] = y
                detection["h"] = h
                detection["inference_time"] = inference_time

                # Add the dictionary to the list of detections
                detections.append(detection)

            # Print detected objects
            #print(f"Detected {class_name} at ({x}, {y}) (inference took {inference_time} ms)")

        # Visualize the results on the frame
        annotated_frame = results[0].plot()

        # Display the annotated frame
        if show_camera:
            cv2.imshow("YOLO Object Detection", annotated_frame)
            cv2.waitKey(1)

    return detections

# Take the list of detected objects and look for one with a specific name
def find_object(detections, name):

    # Look through the list and return a detection if its name matches
    for detection in detections:
        if detection["name"] == name:
            return detection

# Determine if any object is close given the list of detections
def object_within_distance(detections, inches):
    for detection in detections:
        H = detection['h']
        dist = k * d / H
        if dist < inches:
            return True
    return False

# Aim the servos at specified X and Y coordinates in the video feed,
# given the height in pixels (H) and estimated distance from camera (zc)
def aim(X, Y, H):

    # Estimate the distance of the target from the camera using the k constant
    zc = k * d / H

    # Normalize X and Y coordinates
    X = X - CAMERA_WIDTH / 2
    Y = Y - CAMERA_HEIGHT / 2

    # Estimate the horizontal and vertical offset in inches
    xc = X * zc / c
    yc = Y * zc / c

    # Convert from coordinates relative to camera to relative to target
    zt = zc + z_star
    yt = yc + y_star
    xt = xc + x_star

    # Find the yaw and pitch 
    yaw_rad = math.atan(xt / zt)
    pitch_rad = math.atan(yt / zt)
    
    # Convert to degrees
    yaw = math.degrees(yaw_rad)
    pitch = math.degrees(pitch_rad)

    #print(f"Yaw: {yaw:.2f} degrees, Pitch: {pitch:.2f} degrees")

    # Normalize angles so that 0 is center (and invert to match true servo angles)
    yaw = yaw_CENTER - yaw
    pitch = pitch_FORWARD - pitch

    # Move servos
    pan_servo.angle = yaw
    tilt_servo.angle = pitch

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

        # global prev_pos, pos
        # prev_pos = pos
        # pos = msg.pose.pose.position


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
