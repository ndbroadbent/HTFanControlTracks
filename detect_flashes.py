#!/usr/bin/env python3
import cv2
import numpy as np
import matplotlib.pyplot as plt
import AppKit
import os
import sys
import csv

WINDOW_NAME = "Frame"
BRIGHTNESS_THRESHOLD = 180
DIFF_THRESHOLD = 60
FLASH_END_BRIGHTNESS_DIFF = 10
FLASH_MAX_DURATION_MS = 300

# FLASH_OFFSET_MS = 750
FLASH_OFFSET_MS = 0

SHOW_IMAGES = False

video_filename = sys.argv[1]
movie_name = sys.argv[2]
# video_filename = "/Users/ndbroadbent/Downloads/TopGunMaverick.mkv"
# movie_name = "Top Gun Maverick"

brightness_csv_filename = f"Movies/{movie_name}/brightness.csv"
strobe_commands_csv_filename = f"Movies/{movie_name}/detected_flashes.txt"

def formatted_timestamp(timestamp_ms, include_ms=True):
    ms_string = ""
    if include_ms:
        ms_string = f" ({round(timestamp_ms)}ms)"
    return f"{int(timestamp_ms / 1000 / 60 / 60):02d}:{int(timestamp_ms / 1000 / 60 % 60):02d}:{int(timestamp_ms / 1000 % 60):02d}.{int(timestamp_ms % 1000):03d}{ms_string}"

# Parse rows from CSV file if exists
if not os.path.exists(brightness_csv_filename):
    print(f"CSV file not found: {brightness_csv_filename}")
    exit(1)

if not os.path.exists(video_filename):
    print(f"Video file not found: {video_filename}")
    exit(1)

cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
# cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_TOPMOST, 1)

current_frame = 0

# Load the video
cap = cv2.VideoCapture(video_filename)

# Skip ahead to first flash
# cap.set(cv2.CAP_PROP_POS_MSEC, 210000)

framerate = round(cap.get(cv2.CAP_PROP_FPS))
flash_max_frame_count = round(framerate / 1000.0 * FLASH_MAX_DURATION_MS)

print(f"Video framerate (rounded): {framerate}")
print(f"Flash max frame count: {flash_max_frame_count}")

timestamp_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
frame_num = round(cap.get(cv2.CAP_PROP_POS_FRAMES))
print(f"frame_num: {frame_num}")

rolling_average_brightness = 0
previous_brightness = 0
previous_frame = None

flash_start_frame = 0
flash_start_ms = 0
flash_brightness = 0
flash_previous_brightness = 0
flash_previous_frame = None
flash_frame = None
started_flash_detection = False
flash_frame_count = 0

last_timestamp = 0

with open(strobe_commands_csv_filename, 'w', newline='') as commands_csvfile:
    commands_csvwriter = csv.writer(commands_csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)

    with open(brightness_csv_filename, newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        # Skip first row
        next(csvreader)
        for brightness_row in csvreader:
            frame_num = int(brightness_row[0])
            timestamp_ms = int(brightness_row[1])
            brightness = float(brightness_row[3])
            rolling_average_brightness = float(brightness_row[4])

            if not cap.isOpened():
                print("Error opening video stream or file")
                exit(1)

            # Detect bright flashes where the brightness increases sharply,
            # and then quickly returns to the rolling average brightness.
            # Only calculate rolling average brightness when not detecting a flash
            if started_flash_detection:
                flash_frame_count += 1
                if flash_frame_count > flash_max_frame_count:
                    started_flash_detection = False
                    flash_start_ms = 0
                    flash_start_frame = 0
                    continue

                if brightness <= (flash_previous_brightness + FLASH_END_BRIGHTNESS_DIFF):
                    # Confirmed flash
                    flash_duration = timestamp_ms - flash_start_ms
                    print(f"Flash detected!\n" +
                        f"    flash start timestamp: {formatted_timestamp(flash_start_ms)}\n" +
                        f"    flash end timestamp: {formatted_timestamp(timestamp_ms)}\n" +
                        f"    flash duration: {formatted_timestamp(flash_duration)}\n" +
                        f"    flash frame count: {flash_frame_count} / {flash_max_frame_count}\n" +
                        f"    flash brightness: {flash_brightness}\n" +
                        f"    flash previous brightness: {flash_previous_brightness}\n" +
                        f"    current brightness: {brightness}\n")

                    if SHOW_IMAGES:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, flash_start_frame - 2)
                        frame_exists, flash_previous_frame_image = cap.read()
                        if not frame_exists:
                            print("Error reading flash_start_frame")
                            exit(1)
                        cap.set(cv2.CAP_PROP_POS_FRAMES, flash_start_frame - 1)
                        frame_exists, flash_frame_image = cap.read()
                        if not frame_exists:
                            print("Error reading flash_start_frame")
                            exit(1)
                        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num - 1)
                        frame_exists, current_frame_image = cap.read()
                        if not frame_exists:
                            print("Error reading frame")
                            exit(1)

                        stacked_frames = np.vstack((flash_previous_frame_image, flash_frame_image, current_frame_image))
                        cv2.imshow(WINDOW_NAME, stacked_frames)

                        AppKit.NSApplication.sharedApplication().activateIgnoringOtherApps_(1)
                        res = cv2.waitKey(0)
                        # Quit if user presses q
                        if res == ord("q"):
                            break

                    flash_with_offset_ms = flash_start_ms + FLASH_OFFSET_MS
                    commands_csvwriter.writerow([formatted_timestamp(flash_with_offset_ms, None), 'STROBE_FLASH'])

                    started_flash_detection = False
                    flash_start_ms = 0

            elif brightness > BRIGHTNESS_THRESHOLD and (brightness - previous_brightness) > DIFF_THRESHOLD:
                print(f"Started flash detection at: {formatted_timestamp(timestamp_ms)}")
                started_flash_detection = True
                flash_frame_count = 0
                flash_start_frame = frame_num
                flash_start_ms = timestamp_ms
                flash_brightness = brightness
                flash_previous_brightness = previous_brightness

            previous_brightness = brightness

        cv2.destroyAllWindows()
        cap.release()
