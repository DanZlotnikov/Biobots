import ctypes
import os
import time 


try:
    # Folder where THIS Python file is located
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Full path to the DLL in the same folder
    dll_path = os.path.join(base_dir, "DeuteronStimulator.dll")
    stim = ctypes.WinDLL(dll_path)

except Exception as e:
    print("DLL load FAILED:", e)


# int Stim_ConnectToTransmitter()
stim.Stim_ConnectToTransmitter.restype = ctypes.c_int

# int SetTransceiverFrequency(int freq)
stim.SetTransceiverFrequency.argtypes = [ctypes.c_int]
stim.SetTransceiverFrequency.restype = ctypes.c_int

# int EnumerateAndSelectTarget(ref int targetSelected)
stim.EnumerateAndSelectTarget.argtypes = [ctypes.POINTER(ctypes.c_int)]
stim.EnumerateAndSelectTarget.restype = ctypes.c_int

# int Stim_GetBatteryVoltage(ref double volts)
stim.Stim_GetBatteryVoltage.argtypes = [ctypes.POINTER(ctypes.c_double)]
stim.Stim_GetBatteryVoltage.restype = ctypes.c_int

# int FireStimulusByValues(
#     int FirstElectrode,
#     int SecondElectrode,
#     double PhaseWidth,
#     double PulsePeriod,
#     double Amplitude1,
#     double Amplitude2,
#     int PulseCount
# )
stim.FireStimulusByValues.argtypes = [
    ctypes.c_int,     # FirstElectrode
    ctypes.c_int,     # SecondElectrode
    ctypes.c_double,  # PhaseWidth
    ctypes.c_double,  # PulsePeriod
    ctypes.c_double,  # Amplitude1
    ctypes.c_double,  # Amplitude2
    ctypes.c_int      # PulseCount
]
stim.FireStimulusByValues.restype = ctypes.c_int

def connect(freq_hz=917000000):
    result = stim.Stim_ConnectToTransmitter()
    if result != 0:
        print("Connect error:", result)

    print("Setting stim frequency:", freq_hz)
    result = stim.SetTransceiverFrequency(int(freq_hz))
    if result != 0:
        print("Set frequency error:", result)


def fire_stimulus(phase_width, pulse_period, amp, pulse_count):
    # FireStimulusByValues(
    #   int FirstElectrode,
    #   int SecondElectrode,
    #   double PhaseWidth,
    #   double PulsePeriod,
    #   double Amplitude1,
    #   double Amplitude2,
    #   int PulseCount
    # )
    result = stim.FireStimulusByValues(
        1,      # FirstElectrode
        2,      # SecondElectrode
        float(phase_width),
        float(pulse_period),
        float(amp),
        float(amp),
        int(pulse_count)
    )

    if result != 0:
        print("Stim error:", result)


def stimulus_loop():
    # Connect at 917 MHz
    connect(917000000)

    base_amp = 0.000180     # 180 microamp
    amp_diff = 0.0
    rest_time = 1000         # milliseconds
    max_amp = 0.000200        # 200 microamp
    pulse_count = 50

    # Kobayashi fish parameters
    phase_width = 0.0015
    pulse_period = 0.01

    for i in range(15):
        amp = min(base_amp + amp_diff * i, max_amp)

        print(f"Iteration {i}: Stimulating brain with {amp} A")
        fire_stimulus(phase_width, pulse_period, amp, pulse_count)

        print(f"Wait {rest_time} ms")
        time.sleep(rest_time / 1000.0)
