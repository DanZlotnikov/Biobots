import cv2
from gpiozero import LED
import time
import config
from concurrent.futures import ThreadPoolExecutor
import requests

executor = ThreadPoolExecutor(max_workers=2)
led = LED(config.LED_GPIO_PIN)

def draw_movement_overlay(frame):
    """
    Draws a red rectangle with the text 'MOVEMENT DETECTED'
    in the upper-left corner of the frame.
    """

    label = "MOVEMENT DETECTED"

    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 1.2
    thickness = 3

    # Calculate text size
    (tw, th), _ = cv2.getTextSize(label, font, scale, thickness)

    # Rectangle position
    x1, y1 = 10, 10
    x2 = x1 + tw + 20
    y2 = y1 + th + 20

    # Red box
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), -1)

    # White text
    cv2.putText(
        frame,
        label,
        (x1 + 10, y1 + th + 5),
        font,
        scale,
        (255, 255, 255),
        thickness,
        cv2.LINE_AA
    )


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
