# Loads a YOLO model and exports it to a different file format

from ultralytics import YOLO

model = YOLO('./YOLO/Models/test.pt')

# TensorFlow file format
model.export(format='engine')
