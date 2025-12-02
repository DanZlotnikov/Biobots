from flask import Flask, Response
from gpiozero import LED
from picamzero import Camera
import threading
import cv2
import time

app = Flask(__name__)

# ============================
# LED SETUP
# ============================
led = LED(21)

@app.get("/on")
def turn_on():
    led.on()
    return "LED ON"

@app.get("/off")
def turn_off():
    led.off()
    return "LED OFF"

@app.get("/")
def root():
    return "Use /stream, /on, /off"


# ============================
# CAMERA SETUP (PicamZero)
# ============================
cam = Camera()
cam.resolution = (640, 480)     # Lower resolution → much faster stream
cam.framerate = 30

# AWB fix for "everything is blue"
cam.awb_mode = "auto"
time.sleep(1)  # let colors stabilize


# ============================
# SHARED FRAME BUFFER
# ============================
latest_frame = None
lock = threading.Lock()


# ============================
# BACKGROUND CAMERA THREAD
# ============================
def camera_thread():
    global latest_frame

    while True:
        frame = cam.capture_array()
        with lock:
            latest_frame = frame


threading.Thread(target=camera_thread, daemon=True).start()


# ============================
# MJPEG STREAM GENERATOR
# ============================
def generate_frames():
    global latest_frame

    # Faster JPEG encoding parameters
    encode_params = [
        cv2.IMWRITE_JPEG_QUALITY, 80,          # Quality: 0–100
        cv2.IMWRITE_JPEG_OPTIMIZE, 1,          # Optimized Huffman tables
    ]

    while True:
        if latest_frame is None:
            time.sleep(0.005)
            continue

        with lock:
            frame = cv2.cvtColor(latest_frame, cv2.COLOR_RGB2BGR)

        # Fast JPEG encoding
        ret, buffer = cv2.imencode(".jpg", frame, encode_params)
        frame_bytes = buffer.tobytes()

        # MJPEG chunk
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            frame_bytes + b"\r\n"
        )

        time.sleep(0.001)   # reduce CPU load slightly


@app.get("/stream")
def stream():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# ============================
# START SERVER
# ============================
if __name__ == "__main__":
    print("🚀 Server running at http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, threaded=True, debug=False)
