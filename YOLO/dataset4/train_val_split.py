# Use this script to split data into training and validation directories
# Your pictures should be in /images and your labels should be in /labels

import os
import shutil
import random

# Paths to original image and label directories
image_dir = "images"
label_dir = "labels"

# Output directories
train_image_dir = "images/train"
train_label_dir = "labels/train"
val_image_dir = "images/val"
val_label_dir = "labels/val"

# Make the directories if they don't exist already
for folder in [train_image_dir, train_label_dir, val_image_dir, val_label_dir]:
    os.makedirs(folder, exist_ok=True)

# Get list of image files (assuming label filenames match)
image_files = sorted([f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.png'))])
random.shuffle(image_files)

# Define split ratio (pictures used for training / total pictures)
train_ratio = 0.8
split_index = int(len(image_files) * train_ratio)

# Split into training and validation sets
train_files = image_files[:split_index]
val_files = image_files[split_index:]

# Function to move files
def move_files(file_list, src_img_dir, src_lbl_dir, dest_img_dir, dest_lbl_dir):
    for file in file_list:
        img_path = os.path.join(src_img_dir, file)
        lbl_path = os.path.join(src_lbl_dir, os.path.splitext(file)[0] + ".txt")  # Assuming .txt labels

        # Move image
        shutil.move(img_path, os.path.join(dest_img_dir, file))

        # Move corresponding label if it exists
        if os.path.exists(lbl_path):
            shutil.move(lbl_path, os.path.join(dest_lbl_dir, os.path.basename(lbl_path)))

# Move training and validation files
move_files(train_files, image_dir, label_dir, train_image_dir, train_label_dir)
move_files(val_files, image_dir, label_dir, val_image_dir, val_label_dir)

print("Dataset split complete!")
