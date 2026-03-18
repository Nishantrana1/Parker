"""
audio_detector.py — Voice-activity detection helpers.

Provides two pure functions:
    • detect_audio_level()  → float   (RMS of an audio block)
    • is_voice_detected()   → bool    (level vs. threshold)
"""

import numpy as np


def detect_audio_level(audio_data: np.ndarray) -> float:
    """
    Compute the Root-Mean-Square (RMS) volume of an audio block.

    Parameters
    ----------
    audio_data : np.ndarray
        Raw audio samples (1-D or 2-D; multi-channel is flattened).

    Returns
    -------
    float
        RMS value — a non-negative number representing the audio energy.
    """
    if audio_data.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(audio_data.astype(np.float64) ** 2)))


def is_voice_detected(level: float, threshold: float) -> bool:
    """
    Decide whether the measured audio level indicates speech.

    Parameters
    ----------
    level : float
        RMS value returned by detect_audio_level().
    threshold : float
        Minimum RMS to consider as voice activity.

    Returns
    -------
    bool
        True if level >= threshold, False otherwise.
    """
    return level >= threshold
