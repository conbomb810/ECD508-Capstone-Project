# Runs object detection and aims the turret at any detected target in the frame
# Authors: Angelo DiTocco, Connor Meybohm, Julian Stala, Alan Weiss (ECD508)

# Imports for object detection
import cv2
from ultralytics import YOLO
import custom_object_detection as objdet

# Imports for turret
import time
import board
import busio
import adafruit_pca9685
from adafruit_servokit import ServoKit
import adafruit_motor.servo
import math

from pynput import keyboard

# Specify whether to aim on key press or automatically
def __main__():
    # test_with_key_press()
    test_without_key_press()

CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

# Object detection setup
model = YOLO("YOLO/Models/custom_model_5.engine", task="detect")
# Take the RealSense webcam
cap = cv2.VideoCapture("/dev/video4")
cap.set(3, CAMERA_WIDTH)
cap.set(4, CAMERA_HEIGHT)
# Configure exposure to minimize motion blur
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
cap.set(cv2.CAP_PROP_EXPOSURE, 300)

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

pitch_FORWARD = 35
pitch_MIN = 0
pitch_UP = 140
pitch_MAX = 58

yaw_CENTER = 92 
yaw_MIN = 48
yaw_MAX = 136

def aim(X, Y, H):
    
    # constant offsets from camera to turret, play with these for better accuracy
    # also change them if you change the camera mount
    x_star = 0.375
    y_star = 2.25 
    z_star = 4.75

    # diameter of target in inches
    d = 7.125

    # constants from line of best fit
    k = 865.634
    c = 850.381

    # estimate the distance from the target height
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

    # Normalize angles so that 0 is center (and invert to match ServoKit angles)
    yaw = yaw_CENTER - yaw
    pitch = pitch_FORWARD - pitch

    # Move servos
    pan_servo.angle = yaw
    tilt_servo.angle = pitch

	
# Runs camera inference for a certain amount of time to ensure a smooth video feed
def wait(duration):

    start_time = time.time()
    while time.time() - start_time < duration:
        objdet.get_detections(model, cap)
        cv2.waitKey(1)

# Stuff for key press handling:

# Store all the pressed keys in a dictionary
key_states = {}

# Update the dictionary on key press or release
def on_press(key):
    try:
        key_states[key.char] = True  # For alphanumeric keys
    except AttributeError:
        key_states[key] = True  # For special keys

def on_release(key):
    try:
        key_states[key.char] = False
    except AttributeError:
        key_states[key] = False

# Check if a key in the dictionary has a true value
def is_pressed(key):
    return key_states.get(key, False)

# Make a keyboard listener
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

# Main loop to fire turret based on key press
def test_with_key_press():

    print("Press W to fire turret or Q to exit")

    while True:

        # Run custom model to get object detection data
        detections = objdet.get_detections(model, cap)

        # Exit program on Q
        if is_pressed('q'):
            pan_servo.angle = yaw_CENTER
            tilt_servo.angle = pitch_FORWARD
            laser_channel.duty_cycle = 0x0000
            break

        # Fire turret on W
        if is_pressed('w'):

            # If any object is detected
            if detections:

                # Search the list for a target
                target = objdet.find_object(detections, "target")

                if target:

                    # aim and fire at the target
                    X = target["x"]
                    Y = target["y"]
                    H = target['h']
                    aim(X, Y, H)
                    laser_channel.duty_cycle = 0xFFFF
                
                else:
                    laser_channel.duty_cycle = 0x0000
                    print("No target detected")
            
            else:
                print("Nothing detected")

# Main loop to aim turret continuously
def test_without_key_press():

    print("Turret will aim automatically. Press Q to exit")

    while True:

        # Run custom model to get object detection data
        detections = objdet.get_detections(model, cap, True)

        # Exit program on Q
        if is_pressed('q'):
            pan_servo.angle = yaw_CENTER
            tilt_servo.angle = pitch_FORWARD
            laser_channel.duty_cycle = 0x0000
            break

        # If any object is detected
        if detections:

            # Search the list for a target
            target = objdet.find_object(detections, "target")

            if target:

                # aim at the target
                X = target["x"]
                Y = target["y"]
                H = target['h']
                aim(X, Y, H)
                laser_channel.duty_cycle = 0xFFFF


if __name__ == '__main__':
    __main__()
