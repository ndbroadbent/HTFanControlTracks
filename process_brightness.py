#!/usr/bin/env python3
import cv2
import numpy as np
import matplotlib.pyplot as plt
import AppKit
import os
import csv

WINDOW_NAME = "Frame"
BRIGHTNESS_THRESHOLD = 150
DIFF_THRESHOLD = 60
FLASH_END_BRIGHTNESS_DIFF = 5
FLASH_MAX_DURATION_MS = 250

# video_filename = sys.argv[1]
# movie_name = sys.argv[2]
video_filename = "/Users/ndbroadbent/Downloads/Movies/Ready Player One (2018) [WEBRip] [720p] [YTS.AM]/Ready.Player.One.2018.720p.WEBRip.x264-[YTS.AM].mp4"
movie_name = "Ready Player One (2018)"

brightness_csv_filename = f"Movies/{movie_name}/brightness.csv"
strobe_commands_csv_filename = f"Movies/{movie_name}/strobe_commands.txt"

brightness_rows = []

with open(brightness_csv_filename, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    csvwriter.writerow(['frame', 'timestampMs', 'timestamp', 'brightness', 'avgBrightness'])

    # cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    # cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_TOPMOST, 1)

    current_frame = 0

    # Load the video
    cap = cv2.VideoCapture(video_filename)

    # Skip ahead to first flash
    # cap.set(cv2.CAP_PROP_POS_MSEC, 210000)

    framerate = round(cap.get(cv2.CAP_PROP_FPS))
    flash_max_frame_count = round(framerate / 1000.0 * FLASH_MAX_DURATION_MS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    duration_ms = frame_count / framerate * 1000

    print(f"Video framerate (rounded): {framerate}")
    print(f"Flash max frame count: {flash_max_frame_count}")
    print(f"Video frame count: {frame_count}")
    print(f"Video duration (ms): {duration_ms}")

    timestamp_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
    frame_num = round(cap.get(cv2.CAP_PROP_POS_FRAMES))
    print(f"frame_num: {frame_num}")

    rolling_average_brightness = 0

    def formatted_timestamp(timestamp_ms, include_ms=True):
        ms_string = ""
        if include_ms:
            ms_string = f" ({round(timestamp_ms)}ms)"
        return f"{int(timestamp_ms / 1000 / 60 / 60):02d}:{int(timestamp_ms / 1000 / 60 % 60):02d}:{int(timestamp_ms / 1000 % 60):02d}.{int(timestamp_ms % 1000):03d}{ms_string}"

    last_timestamp = 0

    while cap.isOpened():
        frame_exists, frame = cap.read()
        if not frame_exists:
            break

        timestamp_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
        frame_num = cap.get(cv2.CAP_PROP_POS_FRAMES)

        # Print timestamp every 10 seconds
        if timestamp_ms - last_timestamp > 10000:
            processed_percentage = round(timestamp_ms / duration_ms * 100, 1)
            print(f"Timestamp: {formatted_timestamp(timestamp_ms)} ({processed_percentage}%)", end="\r")
            last_timestamp = timestamp_ms

        bgr_brightness = cv2.mean(frame)
        # Calculate perceived brightness of the frame
        brightness = bgr_brightness[0] * 0.114 + bgr_brightness[1] * 0.587 + bgr_brightness[2] * 0.299

        brightness_row = [
            round(frame_num),
            round(timestamp_ms),
            formatted_timestamp(timestamp_ms, include_ms=False),
            round(brightness, 1),
            round(rolling_average_brightness, 1)]
        csvwriter.writerow(brightness_row)

    cap.release()
