import cv2
import numpy as np
import datetime
import time
import os
from collections import deque

from picamzero import Camera  # <--- NEW: live camera source
import config


# ============================
# Output folder setup
# ============================
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_VIDEO = os.path.join(OUTPUT_DIR, "annotated_live_stream.mp4")
OUTPUT_TIMESTAMPS = os.path.join(OUTPUT_DIR, "movement_times.txt")

# Clean old output
if os.path.exists(OUTPUT_VIDEO):
    os.remove(OUTPUT_VIDEO)
if os.path.exists(OUTPUT_TIMESTAMPS):
    os.remove(OUTPUT_TIMESTAMPS)

print(f"Saving annotated video to: {OUTPUT_VIDEO}")
print(f"Saving movement timestamps to: {OUTPUT_TIMESTAMPS}")

movement_times = []


# ============================
# LIVE CAMERA INITIALIZATION
# ============================
cam = Camera()
cam.resolution = (1280, 720)
cam.framerate = 30

# Fix the RGB/BGR inversion problem
# PicamZero returns RGB but OpenCV expects BGR
COLOR_SWAP = True

# Fix blue tint
cam.awb_mode = "auto"
time.sleep(1)
cam.awb_gains = (2.0, 1.3)

print("🎥 Live camera stream started.")


# ============================
# Establish FPS and frame size
# ============================
# Grab one frame to initialize sizes
frame = cam.capture_array()
if COLOR_SWAP:
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

height, width, _ = frame.shape
fps = cam.framerate

print(f"Live Camera FPS: {fps}")
print(f"Resolution: {width} x {height}")


# ============================
# VideoWriter for annotated output
# ============================
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
video_out = cv2.VideoWriter(OUTPUT_VIDEO, fourcc, fps, (width, height))


# ============================
# Background subtractor
# ============================
fgbg = cv2.createBackgroundSubtractorMOG2(
    history=config.MOG2_HISTORY,
    varThreshold=config.MOG2_VAR_THRESHOLD,
    detectShadows=False
)

movement_window = deque(maxlen=config.WINDOW_SIZE)
cooldown_frames = 0
frame_idx = 0
kernel_small = np.ones(config.MORPH_KERNEL_SMALL, np.uint8)

print("🐟 Movement detection active.")

start = time.time()

# ============================
# MAIN LOOP — LIVE STREAM PROCESSING (headless)
# Use Ctrl+C (KeyboardInterrupt) to stop and save outputs
# ============================
try:
    while True:

        # Capture frame from CSI camera
        frame = cam.capture_array()

        # Fix RGB→BGR (critical!)
        if COLOR_SWAP:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        frame_idx += 1
        timestamp_sec = frame_idx / fps

        # Resize for processing
        new_w = int(width * config.SCALE)
        new_h = int(height * config.SCALE)
        small = cv2.resize(frame, (new_w, new_h))

        frame_area_small = new_w * new_h
        MIN_MOV_AREA = frame_area_small * config.AREA_RATIO

        # ===== MASKS =====
        motion_mask = fgbg.apply(small)
        motion_mask = cv2.morphologyEx(motion_mask, cv2.MORPH_OPEN, kernel_small)
        motion_mask = cv2.dilate(motion_mask, None, iterations=1)

        hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
        color_mask = cv2.inRange(hsv, config.ORANGE_LOW, config.ORANGE_HIGH)
        color_mask = cv2.medianBlur(color_mask, config.MEDIAN_BLUR_SIZE)
        color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, kernel_small)

        combined_mask = cv2.bitwise_and(motion_mask, color_mask)
        contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        movement_detected = False
        full_contours = []
        sx = width / new_w
        sy = height / new_h

        for c in contours:
            if cv2.contourArea(c) > MIN_MOV_AREA:
                movement_detected = True
                # upscale contour
                full_contours.append((c.astype(np.float32) * np.array([sx, sy])).astype(np.int32))

        # Sliding window logic
        movement_window.append(1 if movement_detected else 0)
        smoothed_movement = sum(movement_window) >= config.THRESHOLD_COUNT

        if smoothed_movement:
            cooldown_frames = config.COOLDOWN_DURATION
        elif cooldown_frames > 0:
            cooldown_frames -= 1

        # ===== MOVEMENT EVENT =====
        if (smoothed_movement or cooldown_frames > 0) and full_contours:

            ts = str(datetime.timedelta(seconds=timestamp_sec))

            print(f"[LIVE] {ts} — MOVEMENT ({sum(movement_window)}/{config.WINDOW_SIZE})")

            movement_times.append(ts)

            label = f"FISH MOVEMENT ({sum(movement_window)}/{config.WINDOW_SIZE})"
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)

            cv2.rectangle(frame, (10, 10), (20 + tw, 20 + th + 20), (0, 0, 255), -1)
            cv2.putText(frame, label, (20, 20 + th), cv2.FONT_HERSHEY_SIMPLEX,
                        1.5, (255, 255, 255), 3)

        # Save frame to output video
        video_out.write(frame)
except KeyboardInterrupt:
    print("Keyboard interrupt received — stopping live capture and saving outputs...")


# ============================
# SAVE MOVEMENT LOG
# ============================
with open(OUTPUT_TIMESTAMPS, "w") as f:
    for t in movement_times:
        f.write(t + "\n")

video_out.release()
cv2.destroyAllWindows()

print("\n✅ Annotated live-stream video saved.")
print("✅ Movement timestamps saved.")
