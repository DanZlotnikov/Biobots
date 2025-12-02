# output_manager.py
import os
import cv2

class OutputManager:
    def __init__(self, output_dir="output", video_name="annotated_live_stream.mp4", log_name="movement_times.txt"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        self.video_path = os.path.join(output_dir, video_name)
        self.log_path = os.path.join(output_dir, log_name)

        # Clear old files
        if os.path.exists(self.video_path): os.remove(self.video_path)
        if os.path.exists(self.log_path): os.remove(self.log_path)

        # Buffers
        self.frames = []
        self.movement_times = []

    def save_frame(self, frame):
        self.frames.append(frame.copy())

    def record_movement(self, timestamp):
        self.movement_times.append(timestamp)

    def close(self, real_fps, frame_size):
        """Write video at correct FPS and save timestamps."""
        print(f"\nWriting video with real FPS = {real_fps:.2f}")

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        vw = cv2.VideoWriter(self.video_path, fourcc, real_fps, frame_size)

        for f in self.frames:
            vw.write(f)

        vw.release()

        # save timestamps
        with open(self.log_path, "w") as f:
            for t in self.movement_times:
                f.write(t + "\n")

        print("✅ Annotated video saved.")
        print("✅ Movement timestamps saved.")
