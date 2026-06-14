import cv2
import numpy as np
import os

# CHANGE THIS to one of your run folders
DELTA_FOLDER = "frames_20260116_205653"

TOTAL_PIXELS = 1920 * 1080 * 3

total_percentage = 0
delta_count = 0

for filename in os.listdir(DELTA_FOLDER):
    if filename.startswith("delta"):
        img_path = os.path.join(DELTA_FOLDER, filename)
        img = cv2.imread(img_path)

        if img is None:
            continue

        non_zero_values = np.count_nonzero(img)
        percentage = (non_zero_values / TOTAL_PIXELS) * 100

        total_percentage += percentage
        delta_count += 1

# Average percentage across all delta frames
average_percentage = total_percentage / delta_count

print("Number of delta frames:", delta_count)
print("Average % of changed RGB values:", average_percentage)
