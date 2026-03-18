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
SILENCE_DELAY = 2.0

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
