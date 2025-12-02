# detection.py
import cv2
import numpy as np
from collections import deque
import config

class MovementDetector:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.fgbg = cv2.createBackgroundSubtractorMOG2(
            history=config.MOG2_HISTORY,
            varThreshold=config.MOG2_VAR_THRESHOLD,
            detectShadows=False
        )

        self.movement_window = deque(maxlen=config.WINDOW_SIZE)
        self.cooldown_frames = 0

        self.new_w = int(width * config.SCALE)
        self.new_h = int(height * config.SCALE)
        self.kernel_small = np.ones(config.MORPH_KERNEL_SMALL, np.uint8)

        self.min_area = (self.new_w * self.new_h) * config.AREA_RATIO

    def process(self, frame):
        """Returns: (movement_active, contour_list, movement_score)"""

        small = cv2.resize(frame, (self.new_w, self.new_h))

        # Motion
        motion = self.fgbg.apply(small)
        motion = cv2.morphologyEx(motion, cv2.MORPH_OPEN, self.kernel_small)
        motion = cv2.dilate(motion, None, iterations=1)

        # Color
        hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
        color = cv2.inRange(hsv, config.ORANGE_LOW, config.ORANGE_HIGH)
        color = cv2.medianBlur(color, config.MEDIAN_BLUR_SIZE)
        color = cv2.morphologyEx(color, cv2.MORPH_CLOSE, self.kernel_small)

        # Combined
        combined = cv2.bitwise_and(motion, color)
        contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detected = False
        full_contours = []
        sx = self.width / self.new_w
        sy = self.height / self.new_h

        for c in contours:
            if cv2.contourArea(c) > self.min_area:
                detected = True
                full = (c.astype(np.float32) * np.array([sx, sy])).astype(np.int32)
                full_contours.append(full)

        # sliding window smoothing
        self.movement_window.append(1 if detected else 0)
        score = sum(self.movement_window)
        smoothed = score >= config.THRESHOLD_COUNT

        # cooldown logic
        if smoothed:
            self.cooldown_frames = config.COOLDOWN_DURATION
        elif self.cooldown_frames > 0:
            self.cooldown_frames -= 1

        movement_active = smoothed or self.cooldown_frames > 0

        return movement_active, full_contours, score
