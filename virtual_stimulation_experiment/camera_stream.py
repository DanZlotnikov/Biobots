# camera_stream.py
import cv2
import subprocess
import time
import signal
import numpy as np

class LiveCamera:
    def __init__(self, resolution=(640, 360), framerate=30):
        self.width, self.height = resolution
        self.fps = framerate

        # Start rpicam-vid with MJPEG output to stdout
        self.proc = subprocess.Popen([
            "rpicam-vid",
            "-t", "0",
            "-n",
            "--width", str(self.width),
            "--height", str(self.height),
            "--framerate", str(self.fps),
            "--codec", "mjpeg",
            "-o", "-"     # stdout
        ], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

        # Internal buffer for JPEG frame assembly
        self.buffer = b""

        # Warm-up: read first frame
        first = None
        while first is None:
            first = self._read_jpeg_frame()

        # set attributes from first frame
        self.height, self.width, _ = first.shape

    def _read_jpeg_frame(self):
        """Reads MJPEG bytes from stdout, extracts one JPEG, decodes it."""

        while True:
            chunk = self.proc.stdout.read(4096)
            if not chunk:
                return None

            self.buffer += chunk

            start = self.buffer.find(b'\xff\xd8')  # JPEG SOI
            end   = self.buffer.find(b'\xff\xd9')  # JPEG EOI

            if start != -1 and end != -1:
                jpg = self.buffer[start:end+2]
                self.buffer = self.buffer[end+2:]
                self.latest_jpeg = jpg

                # decode
                frame = cv2.imdecode(np.frombuffer(jpg, np.uint8), cv2.IMREAD_COLOR)
                return frame

    def get_frame(self):
        """Returns next decoded frame."""
        return self._read_jpeg_frame()

    def release(self):
        """Stops rpicam-vid cleanly."""
        try:
            self.proc.send_signal(signal.SIGTERM)
        except:
            pass
