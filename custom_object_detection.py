# Script that runs object detection as a function so that it can be referenced by other scripts
# Authors: Angelo DiTocco, Connor Meybohm, Julian Stala, Alan Weiss (ECD508)

import cv2
from ultralytics import YOLO


# Function to run inference and return a list of any detected objects
def get_detections(model, cap, show_camera=True):

    # Make an empty list to store detections (dictionaries)
    detections = []

    # Read a frame from the video
    success, frame = cap.read()

    if success:
        # Run YOLO object detection on the frame
        results = model(frame, verbose=False, conf=0.8)

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
                w = int(boxes.xywh[0][2].item())
                h = int(boxes.xywh[0][3].item())


                # Get the inference time in ms
                inference_time = int(results[0].speed['inference'])

                # Put all that stuff in a dictionary
                detection = {}
                detection["name"] = class_name
                detection["x"] = x
                detection["y"] = y
                detection["w"] = w
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
    
    # Otherwise return nothing
    return None
