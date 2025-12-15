# utils/server.py
import time
from flask import Flask, Response

app = Flask(__name__)

# Camera instance injected from main.py
_camera = None


def set_camera_instance(cam):
    global _camera
    _camera = cam


@app.route("/")
def video_feed():
    """
    Single-client MJPEG stream.
    Always sends the most recent frame only.
    Old frames are dropped.
    """

    def generate():
        while True:
            if _camera is None:
                time.sleep(0.05)
                continue

            jpeg = _camera.get_latest_jpeg()
            if jpeg is None:
                time.sleep(0.01)
                continue

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n"
                + jpeg +
                b"\r\n"
            )

            # Network pacing (prevents client-side buffering)
            time.sleep(0.03)  # ~30 FPS max

    return Response(
        generate(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


def start_flask(host="0.0.0.0", port=5000):
    # Single client → no threading needed
    app.run(host=host, port=port, use_reloader=False)
