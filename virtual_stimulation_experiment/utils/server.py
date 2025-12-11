# server.py
import time
from flask import Flask, Response, stream_with_context
import config

# This will be assigned externally by main.py
camera_instance = None

# =========================================
#  Flask App Setup
# =========================================
app = Flask(__name__)


def set_camera_instance(cam):
    """
    Called from main.py to attach the LiveCamera instance.
    """
    global camera_instance
    camera_instance = cam


# =========================================
#  MJPEG STREAM GENERATOR
# =========================================
def mjpeg_generator():
    """
    Yields JPEG frames as an MJPEG stream.
    """
    global camera_instance

    while True:
        if camera_instance and camera_instance.latest_jpeg:
            try:
                # Standard multipart/x-mixed-replace MJPEG structure
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" +
                    camera_instance.latest_jpeg +
                    b"\r\n"
                )
            except GeneratorExit:
                # Client disconnected
                return

        # Prevents this loop from using 100% CPU
        time.sleep(0.001)


@app.route("/")
def stream():
    """
    Returns an MJPEG response for browser display.
    """
    return Response(
        stream_with_context(mjpeg_generator()),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# =========================================
#  START SERVER (RUN IN BACKGROUND THREAD)
# =========================================
def start_flask():
    """
    Start Flask server in a background thread.

    main.py does:
        threading.Thread(target=start_flask, daemon=True).start()
    """
    app.run(host="0.0.0.0", port=config.LED_FLASK_PORT, debug=False, threaded=True)
