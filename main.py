"""
main.py — Entry point for the Voice-Reactive Sphere Assistant.

Full pipeline:
  1. Detect voice → sphere LISTENING, buffer audio
  2. Silence for 2s → sphere THINKING, transcribe audio
  3. Generate response → sphere SPEAKING, speak reply via TTS
  4. Done → sphere STANDBY
"""

import sys
import time
import threading
import numpy as np
import sounddevice as sd

import config
from audio_detector import detect_audio_level, is_voice_detected
from movement_controller import start_movement, stop_movement
from speech_listener import SpeechListener
from response_engine import generate_response
from sphere_renderer import (
    SphereRenderer,
    STATE_STANDBY, STATE_LISTENING, STATE_THINKING, STATE_SPEAKING,
)

# ── Shared state ──────────────────────────────────────────────────────
_lock             = threading.Lock()
_voice_active     = False
_last_voice_time  = 0.0
_speech_listener  = SpeechListener()
_processing       = False      # True while thinking/speaking (ignore new audio)


# ── Audio callback ────────────────────────────────────────────────────

def _audio_callback(indata: np.ndarray, frames: int,
                     time_info, status) -> None:
    global _voice_active, _last_voice_time

    if status:
        print(f"⚠️  Audio: {status}", file=sys.stderr)

    with _lock:
        if _processing:
            return  # don't record while Parker is thinking/speaking

    level = detect_audio_level(indata)
    detected = is_voice_detected(level, config.VOLUME_THRESHOLD)
    now = time.time()

    with _lock:
        if detected:
            if not _voice_active:
                _speech_listener.start_buffering()
            _voice_active = True
            _last_voice_time = now
            _speech_listener.add_frames(indata)
        else:
            if _voice_active:
                # keep buffering slightly into silence
                _speech_listener.add_frames(indata)
                if (now - _last_voice_time) >= config.SILENCE_DELAY:
                    _voice_active = False
                    _speech_listener.stop_buffering()

    if detected:
        start_movement()


# ── TTS helper ────────────────────────────────────────────────────────

def _speak(text: str) -> None:
    """Speak text using pyttsx3 (blocking)."""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty("rate", 160)
        engine.say(text)
        engine.runAndWait()
    except Exception as exc:
        print(f"⚠️  TTS error: {exc}", file=sys.stderr)


# ── Response pipeline (runs in a thread) ──────────────────────────────

def _process_speech(renderer: SphereRenderer) -> None:
    """Transcribe buffered audio → generate reply → speak it."""
    global _processing

    with _lock:
        _processing = True

    # --- THINKING ---
    renderer.set_state(STATE_THINKING)
    print("  🧠  Transcribing…")

    text = _speech_listener.transcribe()

    if text:
        print(f"  👤  You said: \"{text}\"")
        renderer.show_user_text(text)

        reply = generate_response(text)
        print(f"  🤖  Parker: {reply}")

        # --- SPEAKING ---
        renderer.set_state(STATE_SPEAKING)
        renderer.show_response(reply)
        _speak(reply)
    else:
        print("  ❓  Couldn't recognise speech.")

    # --- back to STANDBY ---
    stop_movement()
    renderer.set_state(STATE_STANDBY)

    with _lock:
        _processing = False


# ── Main loop ─────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 55)
    print("  🤖  Parker — Voice-Reactive Sphere Assistant")
    print("=" * 55)
    print(f"  Threshold    : {config.VOLUME_THRESHOLD}")
    print(f"  Silence delay: {config.SILENCE_DELAY}s")
    print(f"  Sample rate  : {config.SAMPLE_RATE} Hz")
    print(f"  Serial       : {'Enabled' if config.USE_SERIAL else 'Disabled'}")
    print("-" * 55)
    print("  Speak into your microphone — Parker will respond!")
    print("  Close the window or press Escape to quit.\n")

    renderer = SphereRenderer()

    # Startup greeting
    renderer.show_greeting(config.GREETING_TEXT)
    print(f"  🗣️  {config.GREETING_TEXT}\n")
    greeting_thread = threading.Thread(target=_speak,
                                       args=(config.GREETING_TEXT,),
                                       daemon=True)
    greeting_thread.start()

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
                    active      = _voice_active
                    processing  = _processing
                    has_audio   = _speech_listener.has_audio and not _speech_listener.is_buffering

                # Decide sphere state
                if processing:
                    pass  # state managed by _process_speech thread
                elif active:
                    renderer.set_state(STATE_LISTENING)
                elif has_audio and not processing:
                    # Silence detected + buffered audio ready → process
                    t = threading.Thread(target=_process_speech,
                                         args=(renderer,), daemon=True)
                    t.start()
                else:
                    renderer.set_state(STATE_STANDBY)

                running = renderer.tick()

    except KeyboardInterrupt:
        pass
    finally:
        renderer.quit()
        print("\n👋 Shutting down. Goodbye!")


if __name__ == "__main__":
    main()
