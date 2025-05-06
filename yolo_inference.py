# Returns coordinates and bounding box data of objects detected with the YOLO model
# Authors: Angelo DiTocco, Connor Meybohm, Julian Stala, Alan Weiss (ECD508)

import cv2
from ultralytics import YOLO

# Load the custom model
model = YOLO("./YOLO/Models/custom_model_5.engine", task="detect")

# Take the webcam
cap = cv2.VideoCapture("/dev/video4") 
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
# Configure exposure to minimize motion blur
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
cap.set(cv2.CAP_PROP_EXPOSURE, 300)

# Loop through the video frames
while True:
    # Read a frame from the video
    success, frame = cap.read()

    if success:
        # Run YOLO object detection on the frame
        results = model(frame, verbose=False)

        # Get the detected object's box data
        boxes = results[0].boxes

        # If any objects detected...
        if len(boxes) > 0:

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
            inference_time = round(results[0].speed['inference'])

            print(f"Detected {class_name} at ({x}, {y}) with height {h} (inference took {inference_time} ms)")

        # Visualize the results on the frame
        annotated_frame = results[0].plot()

        # Display the annotated frame
        cv2.imshow("YOLO Object Detection", annotated_frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        # Break the loop if the end of the video is reached
        break

# Release the video capture object and close the display window
cap.release()
cv2.destroyAllWindows()
