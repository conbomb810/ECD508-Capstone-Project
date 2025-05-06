# Script to drive around and shoot people
# I mean targets
# Let's stick with targets

# Authors: Angelo DiTocco, Connor Meybohm, Julian Stala, Alan Weiss (ECD508)

# This version brings up the video feed, but it is quite laggy. To run this script, you will need to connect through SSH using the -X argument from a Linux computer (like the mini computer.) 

# This doesn't control the car at all
# You still need to have the bringup launch open

# Imports for joystick node (that's it)
import time
import rclpy
from rclpy.node import Node
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

# Import for camera
import cv2

# Imports for turret
import board
import busio
import adafruit_pca9685
from adafruit_servokit import ServoKit
import adafruit_motor.servo
import math

# RealSense camera path
rs_path = '/dev/video4'

# Set width and height of camera feed to be used in object detection
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

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

# Flag for resetting turret
turret_reset = 0

# Servo values found through testing and RealSense specs
pitch_FORWARD = 35
pitch_MIN = 0
pitch_UP = 140
pitch_MAX = 58

yaw_CENTER = 92
yaw_MIN = 48
yaw_MAX = 136

# Variable used as a start time for timing functions
ts = 0

# Controller inputs
b_pressed, lb_pressed, turret_reset = None, None, None
dpadLR, dpadUD, triggerR = None, None, None

# Main function
def main(args=None):

    # Global variables for controller inputs
    global b_pressed, lb_pressed, turret_reset
    global dpadLR, dpadUD, triggerR

    # Create the joystick node
    rclpy.init()
    joySubscriber = JoySubscriber()
    
    # Create an executor to run the joystick node
    executor = MultiThreadedExecutor()
    executor.add_node(joySubscriber)
    thread = threading.Thread(target=executor.spin, daemon=True)
    thread.start()

    # Initialize servos
    pan_servo.angle = yaw_CENTER
    tilt_servo.angle = pitch_UP - 20
    laser_channel.duty_cycle = 0
    
    # Take the RealSense webcam
    cap = cv2.VideoCapture(rs_path)

    # Set the resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

    # Set the exposure to minimize motion blur
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
    cap.set(cv2.CAP_PROP_EXPOSURE, 260)
    
    # Run the camera in a different thread if necessary
    # other_thread = threading.Thread(target = run_camera(cap), daemon = True)
    # other_thread.start()

    # Main loop
    i = 0
    while(i == 0):

        # Process controller input every tick
        while get_timer() < 0.05:
            pass
        reset_timer()
        
        # Take a frame from the RealSense
        success, frame = cap.read()
        if success:
            cv2.imshow('RealSense Viewer But Faster', frame)
            cv2.waitKey(1)

        # Manual Turret Control :)
        # only works when manual driving deadmans switch is held
        if lb_pressed:
            #left
            if dpadLR > 0:
                if pan_servo.angle >= 176:
                    pan_servo.angle = pan_servo.angle
                else:
                    pan_servo.angle = pan_servo.angle + 4
            #right
            elif dpadLR < 0:
                if pan_servo.angle <= 4:
                    pan_servo.angle = pan_servo.angle
                else:
                    pan_servo.angle = pan_servo.angle - 4
            #up
            if dpadUD > 0:
                if tilt_servo.angle >= 176:
                    tilt_servo.angle = tilt_servo.angle
                else:
                    tilt_servo.angle = tilt_servo.angle + 4
            #down
            elif dpadUD < 0:
                if tilt_servo.angle <= 31:
                    tilt_servo.angle = tilt_servo.angle
                else:
                    tilt_servo.angle = tilt_servo.angle - 4
            
            #reset turret to standing position
            if turret_reset:
                pan_servo.angle = yaw_CENTER
                tilt_servo.angle = pitch_UP - 20

            #fire laser when right trigger is held down
            if triggerR < 0:
                laser_channel.duty_cycle = 0xFFFF
            else:
                laser_channel.duty_cycle = 0x0000

# Run the camera in another thread if necessary
def run_camera(cap):
    while True:
        success, frame = cap.read()
        if success:
            cv2.imshow('RealSense Viewer But Faster', frame)
            cv2.waitKey(1)

# Just in case we need 'em:
def reset_timer():
    global ts
    ts = time.time()

def get_timer():
    global ts
    return time.time() - ts

# Joystick subscriber to process controller input
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

        global b_pressed, lb_pressed, turret_reset
        global dpadLR, dpadUD, triggerR

        #B button
        if msg.buttons[1]:
            b_pressed = True
        else:
            b_pressed = False
        
        #manual deadmans switch
        if msg.buttons[4]:
            lb_pressed = True
        else:
            lb_pressed = False
        
        #grab dpad and right trigger data when lb is pressed
        if lb_pressed:
            dpadLR = msg.axes[6]
            dpadUD = msg.axes[7]
            triggerR = msg.axes[5]

        #X button
        if msg.buttons[2]:
            turret_reset = True
        else:
            turret_reset = False
            

if __name__ == '__main__':
    main()
