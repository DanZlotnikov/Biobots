import time
import threading
import cv2

from utils.camera_stream import LiveCamera
from detection import MovementDetector
from utils.output_manager import OutputManager
import config
import utils.general_utils as general_utils
from utils.server import set_camera_instance, start_flask
from utils.experiment_logger import ExperimentLogger
import stim.stim as stim
import serial


def main():
    # --------------------------------------------------
    # Init
    # --------------------------------------------------
    cam = LiveCamera()
    cam.latest_jpeg = None
    set_camera_instance(cam)

    detector = MovementDetector(cam.width, cam.height)
    output = OutputManager()
    logger = ExperimentLogger()

    logger.log_trial_start()

    # stim.connect()

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
            # 1. LED + AUDIO STIMULATION
            # ==========================================================
            if now >= next_blink_time:
                print(f"💡 Triggering LED blink at t={now:.3f}")

                threading.Thread(
                    target=general_utils.blink_led, daemon=True
                ).start()
                threading.Thread(
                    target=general_utils.make_sound, daemon=True
                ).start()

                logger.log_stimulation("visual+audio")

                response_window_start = now + config.STIM_RESPONSE_WINDOW_START_DELAY
                response_window_end = now + config.STIM_RESPONSE_WINDOW
                waiting_for_response = True
                stimulus_sent = False

                next_blink_time = now + config.STIM_INTERVAL

            # ==========================================================
            # 2. MOVEMENT DETECTION
            # ==========================================================
            movement_active, _, _ = detector.process(frame)

            # ==========================================================
            # 3. SINGLE-SOURCE BEHAVIOR LOGIC
            # ==========================================================
            if movement_active:
                if (
                    waiting_for_response
                    and response_window_start <= now <= response_window_end
                ):
                    # This movement is a RESPONSE
                    logger.log_reaction()

                    if not stimulus_sent:
                        general_utils.send_brain_stimulus()
                        stimulus_sent = True
                else:
                    # This movement is a NORMAL movement
                    logger.log_movement()

            # Response window expired
            if waiting_for_response and now > response_window_end:
                waiting_for_response = False

            # ==========================================================
            # 4. Visualization + streaming
            # ==========================================================
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

        print(
            f"Captured {frame_count} frames in "
            f"{total_time:.2f}s → {real_fps:.2f} FPS"
        )

        output.close(real_fps, frame_size=(cam.width, cam.height))
        logger.close()

        print("Shutdown complete.")


if __name__ == "__main__":
    main()
