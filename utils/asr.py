"""
Audio-to-text transcription via OpenAI Whisper.
Applies math-specific post-processing to the raw transcript.
"""

import os
import tempfile

import openai

import config

# Ordered so more-specific phrases come before their substrings.
# e.g. "x squared" before "squared" to avoid creating "x **2".
_MATH_REPLACEMENTS: list[tuple[str, str]] = [
    ("x squared", "x**2"),
    ("x cubed", "x**3"),
    ("square root of", "sqrt("),
    ("squared", "**2"),
    ("cubed", "**3"),
    ("raised to the power of", "**"),
    ("to the power of", "**"),
    ("raised to the power", "**"),
    ("divided by", "/"),
    ("multiplied by", "*"),
]


def _apply_math_replacements(text: str) -> str:
    """Replace common spoken-math phrases with symbolic equivalents."""
    result = text
    for phrase, replacement in _MATH_REPLACEMENTS:
        result = result.replace(phrase, replacement)
    return result


def transcribe_audio(audio_bytes: bytes, filename: str) -> dict:
    """
    Transcribe raw audio bytes using OpenAI Whisper, then apply math
    post-processing to the transcript.

    Args:
        audio_bytes: Raw bytes of the audio file.
        filename: Original filename — used to determine the file extension
                  that Whisper expects.

    Returns:
        {
            "transcript": str,        # raw Whisper output
            "processed_text": str,    # transcript with math replacements
            "confidence": float,      # estimated 0.0–1.0
        }
    """
    client = openai.OpenAI(api_key=config.OPENAI_API_KEY)

    ext = os.path.splitext(filename)[1].lower() or ".wav"
    tmp_path: str | None = None

    try:
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        with open(tmp_path, "rb") as f:
            response = client.audio.transcriptions.create(
                model=config.WHISPER_MODEL,
                file=f,
            )

        transcript: str = response.text or ""
        processed = _apply_math_replacements(transcript.lower())

        # Whisper doesn't expose a confidence score.
        # Use a heuristic: very short transcripts for non-trivial audio suggest
        # poor recognition; otherwise default to 0.8.
        word_count = len(transcript.split())
        confidence = 0.4 if (len(audio_bytes) > 50_000 and word_count < 3) else 0.8

        return {
            "transcript": transcript,
            "processed_text": processed,
            "confidence": confidence,
        }

    except Exception:
        return {"transcript": "", "processed_text": "", "confidence": 0.0}

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
