# Use this script to train the model

from ultralytics import YOLO

def main():
    # Load YOLO model (pretrained on COCO)
    model = YOLO("yolo11n.pt")

    # Train the model
    model.train(data="yolo_data.yaml", # file specifying the locations of the training and validation sets
                epochs=1, # more epochs, better model! but more training time.
                imgsz=640, # resize all the images
                batch=16, # lower if too memory intensive
                device=0) # use main GPU

if __name__ == '__main__':
    main()

