# main.py
import time
import threading
import cv2

from utils.camera_stream import LiveCamera
from detection import MovementDetector
from utils.output_manager import OutputManager
import config
import utils.general_utils as general_utils
from utils.server import set_camera_instance, start_flask
import stim.stim as stim


def main():
    cam = LiveCamera()
    cam.latest_jpeg = None     # Streamed JPEG (created here)
    set_camera_instance(cam)
    detector = MovementDetector(cam.width, cam.height)
    output = OutputManager()
    # stim.connect()

    # Start Flask server
    threading.Thread(target=start_flask, daemon=True).start()

    start_time = time.time()
    frame_count = 0
    next_blink_time = time.time() + config.STIM_INTERVAL
    response_window_start = 0
    response_window_end = 0
    waiting_for_response = False

    try:
        while True:
            frame = cam.get_frame()
            if frame is None:
                continue

            frame_count += 1
            now = time.time()

            # ==========================================================
            # 1. LED BLINK TRIGGER
            # ==========================================================
            if now >= next_blink_time:
                print(f"💡 Triggering LED blink at t={now:.3f}")
                threading.Thread(target=general_utils.blink_led, daemon=True).start()
                threading.Thread(target=general_utils.make_sound, daemon=True).start()
                response_window_start = now + config.STIM_RESPONSE_WINDOW_START_DELAY
                response_window_end = now + config.STIM_RESPONSE_WINDOW
                waiting_for_response = True
                next_blink_time = now + config.STIM_INTERVAL

            # ==========================================================
            # 2. MOVEMENT DETECTION
            # ==========================================================
            movement_active, _, _ = detector.process(frame)

            if waiting_for_response and response_window_start <= now <= response_window_end:
                if movement_active:
                    print("🐟 Fish responded to LED stimulus!")
                    general_utils.send_brain_stimulus()
                    waiting_for_response = False

            # If window expired
            if waiting_for_response and now > response_window_end:
                waiting_for_response = False

            if movement_active:
                general_utils.draw_movement_overlay(frame)

            ret, jpeg = cv2.imencode(".jpg", frame)
            if ret:
                cam.update_jpeg(jpeg.tobytes())

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
