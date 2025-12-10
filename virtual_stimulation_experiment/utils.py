import cv2
from gpiozero import LED
import time
import config

# LED hardware
led = LED(config.LED_GPIO_PIN)


def draw_movement_label(frame, label):
    """
    Draw a red rectangle with white text label on the frame.
    
    Args:
        frame: OpenCV frame to draw on
        label: Text label to display
    """
    (tw, th), _ = cv2.getTextSize(label,
                                  cv2.FONT_HERSHEY_SIMPLEX,
                                  1.5, 3)

    cv2.rectangle(frame,
                  (10, 10),
                  (20 + tw, 20 + th + 20),
                  (0, 0, 255), -1)

    cv2.putText(frame,
                label,
                (20, 20 + th),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.5,
                (255, 255, 255),
                3)

def send_brain_stimulus():
    executor.submit(_send_brain_stimulus_worker)

def _send_brain_stimulus_worker():
    try:
        requests.get(config.STIM_TRIG_BASE_URL, timeout=2)
    except requests.exceptions.RequestException as e:
        print("Error:", e)


def make_sound():
    executor.submit(_make_sound_worker)

def _make_sound_worker():
    try:
        requests.get(config.MAKE_SOUND_URL, timeout=2)
    except requests.exceptions.RequestException as e:
        print("Error:", e)


def blink_led():
    for _ in range(config.BLINK_COUNT):
        led.on()
        time.sleep(config.BLINK_ON)
        led.off()
        time.sleep(config.BLINK_OFF)