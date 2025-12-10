# main.py
import time
import threading

from camera_stream import LiveCamera
from detection import MovementDetector
from output_manager import OutputManager
import config
import utils
from server import set_camera_instance, start_flask


# =========================================
#                 MAIN
# =========================================
def main():
    # Create camera instance and expose it to Flask
    cam = LiveCamera()
    set_camera_instance(cam)

    detector = MovementDetector(cam.width, cam.height)
    output = OutputManager()

    print("🌐 Web stream available at: http://<pi-ip>:5000/stream")

    # Start Flask server in background
    threading.Thread(target=start_flask, daemon=True).start()

    # FPS measurement
    start_time = time.time()
    frame_count = 0

    # ----------------------------------------
    # LED blinking & stimulus timing state
    # ----------------------------------------
    next_blink_time = time.time() + config.STIM_INTERVAL
    response_window_start = 0
    response_window_end = 0

    waiting_for_response = False     # Window is active?
    window_consumed = False          # Prevent reopening after 1 stimulation

    # ----------------------------------------
    # Main loop
    # ----------------------------------------
    try:
        while True:
            frame = cam.get_frame()
            frame_count += 1
            now = time.time()

            # ===========================================================
            # 1. LED BLINK TRIGGER
            # ===========================================================
            if now >= next_blink_time:
                print(f"💡 Triggering LED blink at t={now:.3f}")
                threading.Thread(target=config.blink_led, daemon=True).start()

                # The response window will open 0.3 seconds after LED blink
                response_window_start = now + 0.3
                response_window_end = response_window_start + config.STIM_RESPONSE_WINDOW

                waiting_for_response = False
                window_consumed = False   # Fresh trial window can open

                next_blink_time = now + config.STIM_INTERVAL

            movement_active, contours, score = detector.process(frame)
            if movement_active:
                print(f"🐟 Movement detected! t={now:.3f}")

            # Fish moved during the 2-second window?
            if waiting_for_response and response_window_start <= now <= response_window_end:
                if active and contours:
                    print("🐟 Fish responded to LED stimulus!")
                    waiting_for_response = False  # Only count once

            # If window expired
            if waiting_for_response and now > response_window_end:
                waiting_for_response = False

            if movement_active and contours:
                utils.draw_movement_overlay(frame, score)

            # Save raw frames always
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
