"""
tts_engine.py — Text-to-Speech engine using Piper TTS.

Wraps the pre-compiled Piper executable (Windows binary).
Text is piped to piper.exe via stdin, raw PCM audio is captured from
stdout, and played back immediately through the speakers using sounddevice.

Falls back to pyttsx3 if Piper is not available.
"""

import os
import struct
import subprocess
import sys

import numpy as np
import sounddevice as sd


class PiperTTS:
    """
    High-quality local TTS using the Piper executable.

    Parameters
    ----------
    exe_path : str
        Absolute path to piper.exe.
    model_path : str
        Absolute path to the .onnx voice model file.
    """

    def __init__(self, exe_path: str, model_path: str):
        self._exe_path = exe_path
        self._model_path = model_path

        # Check that both files exist at startup
        self._available = (
            os.path.isfile(self._exe_path)
            and os.path.isfile(self._model_path)
        )

        if self._available:
            print(f"  ✅  Piper TTS ready  (voice: {os.path.basename(model_path)})")
        else:
            print("  ⚠️  Piper TTS not found — falling back to pyttsx3")
            if not os.path.isfile(self._exe_path):
                print(f"       Missing: {self._exe_path}")
            if not os.path.isfile(self._model_path):
                print(f"       Missing: {self._model_path}")

    # ── Public API ────────────────────────────────────────────────

    def speak(self, text: str) -> None:
        """
        Speak the given text aloud.

        Uses Piper TTS if available, otherwise falls back to pyttsx3.
        """
        if not text:
            return

        if self._available:
            self._speak_piper(text)
        else:
            self._speak_pyttsx3(text)

    # ── Piper implementation ──────────────────────────────────────

    def _speak_piper(self, text: str) -> None:
        """
        Pipe text → piper.exe → raw PCM audio → sounddevice playback.

        Piper outputs 16-bit mono PCM (WAV) to stdout by default.
        We read the WAV header to get the sample rate, then play
        the raw samples through the speakers.
        """
        try:
            # Run piper.exe with --output_raw for headerless PCM
            # or without it to get WAV output.
            # Using WAV output so we can read the sample rate from header.
            proc = subprocess.run(
                [
                    self._exe_path,
                    "--model", self._model_path,
                    "--output-raw",
                ],
                input=text.encode("utf-8"),
                capture_output=True,
                timeout=30,
            )

            if proc.returncode != 0:
                stderr_msg = proc.stderr.decode("utf-8", errors="replace")
                print(f"  ⚠️  Piper error: {stderr_msg}", file=sys.stderr)
                self._speak_pyttsx3(text)  # fallback
                return

            raw_pcm = proc.stdout
            if not raw_pcm:
                print("  ⚠️  Piper returned empty audio", file=sys.stderr)
                return

            # --output-raw gives signed 16-bit LE mono PCM at the
            # model's native sample rate (22050 Hz for high-quality models).
            sample_rate = 22050  # Piper high-quality models use 22050 Hz

            # Convert raw bytes → float32 numpy array for sounddevice
            samples = np.frombuffer(raw_pcm, dtype=np.int16).astype(np.float32)
            samples /= 32768.0  # normalise to [-1, 1]

            # Play audio (blocking — returns when playback finishes)
            sd.play(samples, samplerate=sample_rate, blocksize=2048)
            sd.wait()

        except subprocess.TimeoutExpired:
            print("  ⚠️  Piper TTS timed out", file=sys.stderr)
        except Exception as exc:
            print(f"  ⚠️  Piper TTS error: {exc}", file=sys.stderr)
            self._speak_pyttsx3(text)  # fallback

    # ── Fallback implementation ───────────────────────────────────

    @staticmethod
    def _speak_pyttsx3(text: str) -> None:
        """Fallback TTS using pyttsx3 (in case Piper is not set up)."""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty("rate", 160)
            engine.say(text)
            engine.runAndWait()
        except Exception as exc:
            print(f"  ⚠️  pyttsx3 fallback error: {exc}", file=sys.stderr)
