# main.py
import cv2
import datetime
import time

from camera_stream import LiveCamera
from detection import MovementDetector
from output_manager import OutputManager
import config

def main():
    cam = LiveCamera()
    detector = MovementDetector(cam.width, cam.height)
    output = OutputManager()

    print("🐟 Movement detection active. Press Ctrl+C to stop.")

    # FPS measurement
    start_time = time.time()
    frame_count = 0

    try:
        while True:
            frame = cam.get_frame()
            frame_count += 1

            # real time timestamp
            timestamp_sec = time.time() - start_time
            timestamp_str = str(datetime.timedelta(seconds=timestamp_sec))

            active, contours, score = detector.process(frame)

            if active and contours:
                print(f"[LIVE] {timestamp_str} — MOVEMENT ({score}/{config.WINDOW_SIZE})")
                output.record_movement(timestamp_str)

                label = f"FISH MOVEMENT ({score}/{config.WINDOW_SIZE})"
                (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)
                cv2.rectangle(frame, (10, 10), (20 + tw, 20 + th + 20), (0, 0, 255), -1)
                cv2.putText(frame, label, (20, 20 + th), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)

            # save raw frame
            output.save_frame(frame)

    except KeyboardInterrupt:
        print("\nKeyboard interrupt — finishing up...")

    finally:
        total_time = time.time() - start_time
        real_fps = frame_count / total_time
        print(f"Captured {frame_count} frames in {total_time:.2f}s → {real_fps:.2f} FPS")

        output.close(real_fps, frame_size=(cam.width, cam.height))
        print("Shutdown complete.")


if __name__ == "__main__":
    main()
