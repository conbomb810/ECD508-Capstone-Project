import cv2
import numpy as np
import random
import os
import shutil

def main():

    image_num = 0

    image_dirs = ["images/train", "images/val"]
    label_dirs = ["labels/train", "labels/val"]

    # Find every image in the directories
    for image_dir, label_dir in zip(image_dirs, label_dirs):
        for image_name in os.listdir(image_dir):

            # If images have already been blurred, stop the program
            if "blurred" in image_name:
                print("Images already blurred. Quitting")
                break

            if image_name.endswith(".png") or image_name.endswith(".jpg"):

                image_path = image_dir + "/" + image_name

                # Get the filename without the extension
                base_filename = os.path.basename(image_path).split('.')[0]

                # Find the same filename in the label directory
                label_path = label_dir + "/" + base_filename + ".txt"

                create_blurred_copy(image_path, label_path)
                
                image_num += 1
                print(f"Processed {image_num} images", end='\r', flush=True)

def create_blurred_copy(image_path, label_path):

    # Pick a random kernel size, correlating to the intensity of the motion blur
    kernel_size = random.randint(60, 120)

    # Make the empty kernel
    kernel = np.zeros((kernel_size, kernel_size))

    # Apply motion blur in a random direction (vertical, horizontal, or either diagonal)
    direction = random.choice(["H", "V", "TLBR", "BLTR"])
    if direction == "H":
        # Fill the middle row with ones (every column)
        kernel[int(kernel_size/2), :] = np.ones(kernel_size)
    elif direction == "V":
        # Fill the middle column with ones (every row)
        kernel[:, int(kernel_size/2)] = np.ones(kernel_size)
    elif direction == "TLBR":
        # Go from top left to bottom right
        for i in range(0, kernel_size):
            kernel[i, i] = 1
    elif direction == "BLTR":
        # Go from bottom left to top right
        for i in range(0, kernel_size):
            kernel[kernel_size - 1 - i, i] = 1

    # Normalize the kernel
    kernel /= kernel_size

    # Load the image
    image = cv2.imread(image_path)

    # Apply the filter
    image_blurred = cv2.filter2D(image, -1, kernel)

    # Get the filenames for the blurred copies
    image_path_no_ext = image_path.rpartition('.')[0]
    image_path_blurred = image_path_no_ext + "_blurred.jpg"

    label_path_no_ext = label_path.rpartition('.')[0]
    label_path_blurred = label_path_no_ext + "_blurred.txt"

    # Save the image
    cv2.imwrite(image_path_blurred, image_blurred)

    # Copy the label file
    shutil.copyfile(label_path, label_path_blurred)

if __name__ == "__main__":
    main()
