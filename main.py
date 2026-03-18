"""
main.py — Entry point for the Voice-Reactive Sphere Assistant.

Opens a continuous microphone stream, analyses each audio block for voice
activity (with a 2-second silence delay), drives the visual particle sphere,
and speaks a greeting on startup.
"""

import sys
import time
import threading
import numpy as np
import sounddevice as sd

import config
from audio_detector import detect_audio_level, is_voice_detected
from movement_controller import start_movement, stop_movement
from sphere_renderer import SphereRenderer


# ── Shared state ──────────────────────────────────────────────────────
_voice_active   = False
_last_voice_time = 0.0
_lock            = threading.Lock()


# ── Audio callback ────────────────────────────────────────────────────

def _audio_callback(indata: np.ndarray, frames: int,
                     time_info, status) -> None:
    global _voice_active, _last_voice_time

    if status:
        print(f"⚠️  Audio stream warning: {status}", file=sys.stderr)

    level = detect_audio_level(indata)
    detected = is_voice_detected(level, config.VOLUME_THRESHOLD)

    now = time.time()

    with _lock:
        if detected:
            _voice_active = True
            _last_voice_time = now
        else:
            # Only go idle after SILENCE_DELAY seconds of quiet
            if _voice_active and (now - _last_voice_time) >= config.SILENCE_DELAY:
                _voice_active = False

    if detected:
        start_movement()
    elif not _voice_active:
        stop_movement()


# ── Greeting (text-to-speech in background) ──────────────────────────

def _speak_greeting():
    """Speak the greeting using pyttsx3 (runs in a daemon thread)."""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty("rate", 160)
        engine.say(config.GREETING_TEXT)
        engine.runAndWait()
    except Exception as exc:
        print(f"⚠️  TTS not available: {exc}", file=sys.stderr)


# ── Main loop ─────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 55)
    print("  🤖  Voice-Reactive Sphere Assistant  (Parker)")
    print("=" * 55)
    print(f"  Threshold    : {config.VOLUME_THRESHOLD}")
    print(f"  Silence delay: {config.SILENCE_DELAY}s")
    print(f"  Sample rate  : {config.SAMPLE_RATE} Hz")
    print(f"  Block size   : {config.BLOCK_SIZE} frames")
    print(f"  Serial       : {'Enabled' if config.USE_SERIAL else 'Disabled'}")
    print("-" * 55)
    print("  Speak into your microphone — the sphere will react!")
    print("  Close the window or press Escape to quit.\n")

    renderer = SphereRenderer()

    # Show & speak the greeting
    renderer.show_greeting(config.GREETING_TEXT)
    print(f"  🗣️  {config.GREETING_TEXT}\n")
    tts_thread = threading.Thread(target=_speak_greeting, daemon=True)
    tts_thread.start()

    try:
        with sd.InputStream(
            samplerate=config.SAMPLE_RATE,
            blocksize=config.BLOCK_SIZE,
            channels=1,
            dtype="float32",
            callback=_audio_callback,
        ):
            running = True
            while running:
                with _lock:
                    active = _voice_active
                renderer.set_active(active)
                running = renderer.tick()

    except KeyboardInterrupt:
        pass
    finally:
        renderer.quit()
        print("\n👋 Shutting down. Goodbye!")


if __name__ == "__main__":
    main()
