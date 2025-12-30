# ============================
# Fish Detector Config
# ============================

# Camera
CAMERA_INDEX = 0

# Scaling
SCALE = 0.6

# Movement area ratio
AREA_RATIO = 0.001

# Color (HSV) for orange fish
ORANGE_LOW  = (0, 50, 40)
ORANGE_HIGH = (28, 255, 255)

# Background subtractor
MOG2_HISTORY = 100
MOG2_VAR_THRESHOLD = 4

# Morphology
MORPH_KERNEL_SMALL = (5, 5)
MEDIAN_BLUR_SIZE = 7

# Sliding window smoothing
WINDOW_SIZE = 15
THRESHOLD_COUNT = 12

# Cooldown frames
COOLDOWN_DURATION = 3

# ============================
# LED Config
# ============================
LED_COM_PORT = "COM3" 
LED_BAUDRATE = 115200

# LED blinking timing parameters
STIM_INTERVAL = 5     # every 5 seconds start blinking
BLINK_ON = 0.3
BLINK_OFF = 0.3
BLINK_COUNT = 3
STIM_RESPONSE_WINDOW = 3       # fish has 2 seconds to respond
STIM_RESPONSE_WINDOW_START_DELAY = 1.0  # after LED blink

# ============================
# Windows Stimulator API Config
# ============================
STIM_TRIG_BASE_URL = "http://172.20.10.2:5555/stim"
MAKE_SOUND_URL = "http://172.20.10.2:5555/make_sound"