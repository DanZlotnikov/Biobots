# main.py
import time
import threading
import cv2

from camera_stream import LiveCamera
from detection import MovementDetector
from output_manager import OutputManager
import config
import utils
from server import set_camera_instance, start_flask


def main():
    # -------------------------------
    # Initialize camera + components
    # -------------------------------
    cam = LiveCamera()
    cam.latest_jpeg = None     # Streamed JPEG (created here)

    set_camera_instance(cam)

    detector = MovementDetector(cam.width, cam.height)
    output = OutputManager()

    print("🌐 Web stream available at: http://<pi-ip>:5000/stream")

    # Start Flask server
    threading.Thread(target=start_flask, daemon=True).start()

    start_time = time.time()
    frame_count = 0

    # ----------------------------------------
    # LED blinking & stimulus timing state
    # ----------------------------------------
    next_blink_time = time.time() + config.STIM_INTERVAL
    response_window_start = 0
    response_window_end = 0

    waiting_for_response = False
    window_consumed = False

    # ----------------------------------------
    # Main loop
    # ----------------------------------------
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
                threading.Thread(target=utils.blink_led, daemon=True).start()
                utils.make_sound()
                response_window_start = now + 0.3
                response_window_end = response_window_start + config.STIM_RESPONSE_WINDOW
                waiting_for_response = True
                next_blink_time = now + config.STIM_INTERVAL

            # ==========================================================
            # 2. MOVEMENT DETECTION
            # ==========================================================
            movement_active, _, _ = detector.process(frame)

            if waiting_for_response and response_window_start <= now <= response_window_end:
                if movement_active:
                    print("🐟 Fish responded to LED stimulus!")
                    utils.send_brain_stimulus()
                    waiting_for_response = False

            # If window expired
            if waiting_for_response and now > response_window_end:
                waiting_for_response = False

            # ==========================================================
            # 3. DRAW OVERLAY (movement box)
            # ==========================================================
            if movement_active:
                utils.draw_movement_overlay(frame)

            # ==========================================================
            # 4. Encode frame for MJPEG stream
            # ==========================================================
            ret, jpeg = cv2.imencode(".jpg", frame)
            if ret:
                cam.latest_jpeg = jpeg.tobytes()

            # ==========================================================
            # 5. Save annotated frame
            # ==========================================================
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
