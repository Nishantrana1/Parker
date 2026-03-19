"""
config.py — Central configuration for the Voice-Reactive Sphere Assistant.
"""

# ──────────────────────────────────────────────
#  Audio Settings
# ──────────────────────────────────────────────

# RMS volume level that counts as "someone is speaking".
# Lowered to pick up normal conversational speech, not just loud sounds.
VOLUME_THRESHOLD = 0.005

# Samples per second
SAMPLE_RATE = 16000

# Number of frames per callback block
BLOCK_SIZE = 1024

# How many seconds of silence to wait before transitioning to idle.
SILENCE_DELAY = 1.0

# ──────────────────────────────────────────────
#  Greeting
# ──────────────────────────────────────────────
GREETING_TEXT = "Hello Sir, how can I help you today!"

# ──────────────────────────────────────────────
#  Serial / Arduino Settings  (optional)
# ──────────────────────────────────────────────
USE_SERIAL = False
SERIAL_PORT = "COM3"
SERIAL_BAUD_RATE = 9600

# ──────────────────────────────────────────────
#  Speech-to-Text  (faster-whisper)
# ──────────────────────────────────────────────

# Model size: "tiny", "base", "small", "medium", "large-v3"
# "base" is the sweet spot for real-time robot use (fast + accurate).
WHISPER_MODEL_SIZE = "base"

# "cpu" for CPU-only, "cuda" if you have an NVIDIA GPU.
WHISPER_DEVICE = "cpu"

# Quantisation: "int8" is fastest on CPU, "float16" for GPU.
WHISPER_COMPUTE_TYPE = "int8"

# ──────────────────────────────────────────────
#  Text-to-Speech  (Piper TTS)
# ──────────────────────────────────────────────

import os as _os
_PROJECT_DIR = _os.path.dirname(_os.path.abspath(__file__))

# Path to the Piper executable (Windows pre-compiled binary).
PIPER_EXE_PATH = _os.path.join(_PROJECT_DIR, "piper", "piper", "piper.exe")

# Path to the ONNX voice model file. (UPDATED TO MEDIUM)
PIPER_MODEL_PATH = _os.path.join(_PROJECT_DIR, "piper", "en_US-amy-medium.onnx")