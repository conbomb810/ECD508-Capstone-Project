# Project Description
 Our project is a 1/10th scale RC car that can autonomously drive around a walled track using LiDAR data processed in a deep convolutional network called TinyLidarNet, developed by a Kansas State University team, whose citation can be found at the end of this file. This repository also uses the ROS 2 humble version of the F1Tenth driver stack, which has been modified to use a laser_filters node. The car is also capable of using a custom trained YOLO model to detect and react to stop signs and targets, example images of which can be found in the repository. Additionally, the car has a mounted laser diode turret that will aim at a detected target and turn on the laser. There are multiple top level files, accounting for each of these capabilities, so if your car does not have the proper set up, you can simply run a different top level file. These top level files will be described in the "Directions to Run the Car" section. The operating system used for the project is Ubuntu 22.04, and uses ROS 2 Humble Hawksbill.

# Hardware
The ECD508 autonomous car uses the following hardware:
- Traxxas Slash 4x4 Chassis / Drive Train
- NVIDIA Jetson Orin Nano
- Intel RealSense D435i Depth Camera
- Hokuyo UST-10LX LiDAR
- VESC 6 MkVI
- Logitech F710 controller
- Adafruit PCA9685 Servo Driver
- MG996R Servos (with pan/tilt brackets)
- Laser Diode
- Traxxas 5000mAh LiPo battery
- Talentcell 17500mAh Li-ion battery pack

# ROS 2 Installation
This project was designed for ROS 2 Humble, whose source files are not included. Installation instructions can be found [here](https://docs.ros.org/en/humble/Installation.html).

# Directions to Run the Car
Clone the repository and open two terminals. On the first, run the following commands:
```
cd ECD508-Capstone-Project
. source.bash
ros2 launch f1tenth_stack bringup_launch_new.py
```
This allows for manual control of the car. Confirm that this works by holding down LB and using the analog sticks to drive and steer the car.

Then, on the second terminal, run the top-level file:
```
cd ECD508-Capstone-Project
. source.bash
python3 top_level.py
```
Once this is done initializing, holding RB should allow the car to drive by itself and detect objects.

## Different Top-Level Files
The script `top_level.py` integrates base autonomous driving, object detection, and turret control.

The script `tln_inference.py` is for base autonomous driving only

The script `drive_around_and_annoy_people_no_video.py` is for manual control of the turret only (no autonomous driving).
