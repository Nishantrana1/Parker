"""
speech_listener.py — Audio buffering and speech-to-text transcription.

Buffers raw audio frames while the user speaks.  After silence is detected,
converts the buffer to WAV and sends it to Google Speech Recognition.
"""

import io
import wave
import numpy as np
import speech_recognition as sr

import config


class SpeechListener:
    """Collects audio frames and transcribes them."""

    def __init__(self):
        self._recognizer = sr.Recognizer()
        self._buffer: list[np.ndarray] = []
        self._is_buffering = False

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

    def transcribe(self) -> str:
        """
        Convert the buffered audio to text using Google Speech Recognition.

        Returns the transcribed string, or "" if recognition failed.
        """
        if not self._buffer:
            return ""

        # Concatenate all buffered frames into one array
        audio = np.concatenate(self._buffer, axis=0)
        self._buffer.clear()

        # Convert float32 [-1, 1] → int16
        audio_int16 = (audio * 32767).astype(np.int16)

        # Write to an in-memory WAV file
        wav_io = io.BytesIO()
        with wave.open(wav_io, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(config.SAMPLE_RATE)
            wf.writeframes(audio_int16.tobytes())
        wav_io.seek(0)

        # Feed to speech_recognition
        try:
            with sr.AudioFile(wav_io) as source:
                audio_data = self._recognizer.record(source)
            text = self._recognizer.recognize_google(
                audio_data, language=config.SPEECH_LANGUAGE
            )
            return text.strip()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            print(f"⚠️  Speech Recognition API error: {e}")
            return ""
        except Exception as e:
            print(f"⚠️  Transcription error: {e}")
            return ""
