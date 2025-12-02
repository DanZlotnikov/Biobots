import cv2
import subprocess
import time
import signal
import numpy as np

WIDTH = 640
HEIGHT = 360
FPS = 30
DURATION = 5
OUTPUT = "output.mp4"

print("Starting rpicam-vid (MJPEG)...")

cmd = [
    "rpicam-vid",
    "-t", "0",
    "-n",
    "--width", str(WIDTH),
    "--height", str(HEIGHT),
    "--framerate", str(FPS),
    "--codec", "mjpeg",
    "-o", "-",               # output to stdout (pipe)
]

proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)

print("Reading MJPEG stream...")

# OpenCV VideoWriter
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
writer = cv2.VideoWriter(OUTPUT, fourcc, FPS, (WIDTH, HEIGHT))

start = time.time()
frames = 0
buffer = b""

while True:
    # Read raw bytes
    chunk = proc.stdout.read(1024)
    if not chunk:
        break

    buffer += chunk

    # Look for JPEG frame boundaries
    start_idx = buffer.find(b'\xff\xd8')   # JPEG SOI
    end_idx   = buffer.find(b'\xff\xd9')   # JPEG EOI

    if start_idx != -1 and end_idx != -1:
        jpg = buffer[start_idx:end_idx+2]
        buffer = buffer[end_idx+2:]

        # Decode JPEG → image
        img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

        if img is None:
            continue

        frames += 1
        writer.write(img)

    if time.time() - start >= DURATION:
        break

print("Stopping rpicam-vid...")
proc.send_signal(signal.SIGTERM)

writer.release()
print(f"Saved {OUTPUT}")
print(f"Frames captured: {frames}, approx FPS: {frames/DURATION:.1f}")
