"""
response_engine.py — Rule-based response generator for Parker.

Matches keywords in the user's speech and returns a contextual reply.
Easily extendable — just add more entries to _RULES or swap in an LLM later.
"""

import datetime
import random


def generate_response(user_text: str) -> str:
    """
    Given the transcribed user text, return Parker's reply.

    Parameters
    ----------
    user_text : str
        What the user said (lowercase is handled internally).

    Returns
    -------
    str
        Parker's spoken reply.
    """
    text = user_text.lower().strip()

    if not text:
        return "I'm sorry Sir, I didn't catch that. Could you repeat?"

    # ── Greetings ─────────────────────────────────────────────────
    if _match(text, ["hello", "hi", "hey", "good morning", "good evening",
                      "good afternoon", "good night"]):
        hour = datetime.datetime.now().hour
        if hour < 12:
            greeting = "Good morning"
        elif hour < 17:
            greeting = "Good afternoon"
        elif hour < 21:
            greeting = "Good evening"
        else:
            greeting = "Good night"
        return f"{greeting} Sir! How can I help you?"

    # ── Time ──────────────────────────────────────────────────────
    if _match(text, ["what time", "current time", "time is it",
                      "tell me the time", "what's the time"]):
        now = datetime.datetime.now()
        hour = now.hour
        minute = now.minute
        period = "AM" if hour < 12 else "PM"
        display_hour = hour if hour <= 12 else hour - 12
        if display_hour == 0:
            display_hour = 12
        if minute == 0:
            return f"Sir, it's {display_hour} o'clock {period}."
        else:
            return f"Sir, it's {display_hour}:{minute:02d} {period}."

    # ── Date ──────────────────────────────────────────────────────
    if _match(text, ["what date", "today's date", "what day",
                      "current date", "what's the date"]):
        now = datetime.datetime.now()
        return f"Sir, today is {now.strftime('%A, %B %d, %Y')}."

    # ── Identity ──────────────────────────────────────────────────
    if _match(text, ["what is your name", "what's your name", "who are you",
                      "your name"]):
        return "I'm Parker, your personal assistant, Sir."

    # ── Say my name ──────────────────────────────────────────────────
    if _match(text, ["Say my name"]):
        return "You are Nishant!. Sir."
    # ── How are you ───────────────────────────────────────────────
    if _match(text, ["how are you", "how do you do", "how you doing"]):
        return random.choice([
            "I'm doing great, Sir! Ready to assist you.",
            "All systems operational, Sir. How can I help?",
            "Functioning perfectly, Sir. What do you need?",
        ])

    # ── Thank you ─────────────────────────────────────────────────
    if _match(text, ["thank you", "thanks", "thank"]):
        return random.choice([
            "You're welcome, Sir!",
            "My pleasure, Sir!",
            "Anytime, Sir!",
        ])

    # ── Goodbye ───────────────────────────────────────────────────
    if _match(text, ["goodbye", "bye", "see you", "good night"]):
        return "Goodbye, Sir! I'll be here whenever you need me."

    # ── Jokes ─────────────────────────────────────────────────────
    if _match(text, ["tell me a joke", "joke", "make me laugh",
                      "something funny"]):
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs, Sir!",
            "I told my computer I needed a break. Now it won't stop sending me vacation ads, Sir!",
            "Why was the robot so tired? Because it had a hard drive, Sir!",
        ]
        return random.choice(jokes)

    # ── Help ──────────────────────────────────────────────────────
    if _match(text, ["help", "what can you do", "capabilities"]):
        return ("I can tell you the time, date, tell jokes, "
                "and have a conversation with you, Sir. "
                "More features are coming soon!")

    # ── Weather (placeholder) ─────────────────────────────────────
    if _match(text, ["weather", "temperature", "forecast"]):
        return ("I'm sorry Sir, I don't have weather data connected yet. "
                "That feature is coming soon!")

    # ── Compliments ───────────────────────────────────────────────
    if _match(text, ["you're great", "you're amazing", "good job",
                      "well done", "nice", "awesome"]):
        return "Thank you Sir! I appreciate that."

    # ── Fallback ──────────────────────────────────────────────────
    fallbacks = [
        f"I heard you say \"{user_text}\". I'm still learning, Sir. I'll be smarter soon!",
        f"Interesting, Sir. You said \"{user_text}\". I'll keep that in mind!",
        f"I understand you said \"{user_text}\", but I'm not sure how to help with that yet, Sir.",
    ]
    return random.choice(fallbacks)


def _match(text: str, keywords: list[str]) -> bool:
    """Return True if any keyword appears in text."""
    return any(kw in text for kw in keywords)
