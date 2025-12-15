# camera_stream.py
import cv2
from collections import deque

class LiveCamera:
    def __init__(self, camera_index=1, resolution=(640, 360), framerate=30):
        self.width, self.height = resolution
        self.fps = framerate
        self.jpeg_buffer = deque(maxlen=1)

        # Open USB webcam
        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)

        # Set resolution and FPS (best effort)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,  self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS,          self.fps)

        # Try reading the first frame
        ok, frame = self.cap.read()
        if not ok or frame is None:
            raise RuntimeError("❌ Failed to read from USB camera")

        # Update actual resolution from camera
        self.height, self.width = frame.shape[:2]

    def get_frame(self):
        """Return next frame from USB webcam."""
        ok, frame = self.cap.read()
        if not ok:
            return None
        return frame

    def release(self):
        """Release the webcam."""
        try:
            self.cap.release()
        except:
            pass
        
    def update_jpeg(self, jpeg_bytes):
        self.jpeg_buffer.append(jpeg_bytes)

    def get_latest_jpeg(self):
        if not self.jpeg_buffer:
            return None
        return self.jpeg_buffer[-1]