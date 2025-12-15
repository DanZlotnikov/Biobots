# utils/output_manager.py
import cv2
import os
import time


class OutputManager:
    def __init__(self, output_dir="output"):
        os.makedirs(output_dir, exist_ok=True)

        ts = time.strftime("%Y%m%d_%H%M%S")
        self.video_path = os.path.join(output_dir, f"recording_{ts}.mp4")

        self.writer = None
        self.frame_size = None
        self.fps = 30  # temporary, corrected on close()

    def save_frame(self, frame):
        # Lazy init so we don't allocate until first frame
        if self.writer is None:
            h, w = frame.shape[:2]
            self.frame_size = (w, h)

            self.writer = cv2.VideoWriter(
                self.video_path,
                cv2.VideoWriter_fourcc(*"mp4v"),
                self.fps,
                self.frame_size
            )

        # IMPORTANT: write immediately, never store
        self.writer.write(frame)

    def close(self, real_fps, frame_size=None):
        if self.writer is None:
            return

        self.writer.release()
        self.writer = None

        # Optional: fix FPS after capture
        if real_fps and real_fps > 0:
            self._rewrite_with_correct_fps(real_fps)

    def _rewrite_with_correct_fps(self, real_fps):
        temp_path = self.video_path + ".tmp.mp4"

        cap = cv2.VideoCapture(self.video_path)
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        writer = cv2.VideoWriter(
            temp_path,
            cv2.VideoWriter_fourcc(*"mp4v"),
            real_fps,
            (w, h)
        )

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            writer.write(frame)

        cap.release()
        writer.release()

        os.replace(temp_path, self.video_path)
