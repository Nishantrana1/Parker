"""
speech_listener.py — Audio buffering and speech-to-text transcription.

Buffers raw audio frames while the user speaks.  After silence is detected,
converts the buffer to a temporary WAV file and transcribes it using
faster-whisper (fully local, no internet required).
"""

import io
import wave
import numpy as np

import config


class SpeechListener:
    """
    Collects audio frames and transcribes them using a pre-loaded
    faster-whisper model.

    Parameters
    ----------
    whisper_model : faster_whisper.WhisperModel
        A model instance created **once** at application startup.
        Passed in so the heavy model load happens only once.
    """

    def __init__(self, whisper_model):
        # Store the pre-loaded model (no reloading per transcription)
        self._model = whisper_model
        self._buffer: list[np.ndarray] = []
        self._is_buffering = False

    # ── Buffering controls ────────────────────────────────────────

    def start_buffering(self) -> None:
        """Begin collecting audio frames (call when voice starts)."""
        if not self._is_buffering:
            self._buffer.clear()
            self._is_buffering = True

    def add_frames(self, audio_data: np.ndarray) -> None:
        """Append a block of audio data to the buffer."""
        if self._is_buffering:
            self._buffer.append(audio_data.copy())

    def stop_buffering(self) -> None:
        """Stop collecting frames."""
        self._is_buffering = False

    @property
    def is_buffering(self) -> bool:
        return self._is_buffering

    @property
    def has_audio(self) -> bool:
        return len(self._buffer) > 0

    # ── Transcription ─────────────────────────────────────────────

    def transcribe(self) -> str:
        """
        Convert the buffered audio to text using faster-whisper.

        Returns the transcribed string, or "" if recognition failed.
        """
        if not self._buffer:
            return ""

        # 1. Concatenate all buffered frames into one contiguous array
        audio = np.concatenate(self._buffer, axis=0)
        self._buffer.clear()

        # 2. Convert float32 [-1, 1] → int16 PCM for WAV encoding
        audio_int16 = (audio * 32767).astype(np.int16)

        # 3. Write to an in-memory WAV file
        wav_io = io.BytesIO()
        with wave.open(wav_io, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)                # 16-bit
            wf.setframerate(config.SAMPLE_RATE)
            wf.writeframes(audio_int16.tobytes())
        wav_io.seek(0)

        # 4. Transcribe with faster-whisper
        #    - beam_size=1 for maximum speed (greedy decoding)
        #    - language="en" to skip language detection overhead
        try:
            segments, _info = self._model.transcribe(
                wav_io,
                beam_size=1,
                language="en",
                vad_filter=True,       # skip silence segments
            )
            # Collect all segment texts into one string
            text = " ".join(seg.text.strip() for seg in segments)
            return text.strip()

        except Exception as e:
            print(f"⚠️  Transcription error: {e}")
            return ""
