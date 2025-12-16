import cv2
import config
import winsound
import serial
import time

ser = serial.Serial(config.LED_COM_PORT, config.LED_BAUDRATE, timeout=1)

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
    print("Sending brain stimulus trigger...")


def make_sound():
    winsound.Beep(500, 1000)  # frequency (Hz), duration (ms)


def blink_led():
    for _ in range(config.BLINK_COUNT):
        ser.write(b"ON\n")
        time.sleep(config.BLINK_ON)
        ser.write(b"OFF\n")
        time.sleep(config.BLINK_OFF)
