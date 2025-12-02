# ============================
# Fish Detector Config
# ============================

# Camera
CAMERA_INDEX = 0

# Scaling
SCALE = 0.4

# Movement area ratio
AREA_RATIO = 0.001

# Color (HSV) for orange fish
ORANGE_LOW  = (0, 50, 40)
ORANGE_HIGH = (28, 255, 255)

# Background subtractor
MOG2_HISTORY = 50
MOG2_VAR_THRESHOLD = 4

# Morphology
MORPH_KERNEL_SMALL = (3, 3)
MEDIAN_BLUR_SIZE = 5

# Sliding window smoothing
WINDOW_SIZE = 30
THRESHOLD_COUNT = 15

# Cooldown frames
COOLDOWN_DURATION = 10


# ============================
# LED Config
# ============================

LED_FLASK_PORT = 5000
LED_GPIO_PIN = 21

BLINK_COUNT = 3
BLINK_DURATION = 0.2  # seconds