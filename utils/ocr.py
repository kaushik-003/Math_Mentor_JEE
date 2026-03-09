"""
Image-to-text extraction via GPT-4o Vision.
"""

import base64
import json

import openai

import config


def _detect_mime_type(image_bytes: bytes) -> str:
    """Infer MIME type from magic bytes."""
    if image_bytes[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    return "image/jpeg"


def extract_text_from_image(image_bytes: bytes) -> dict:
    """
    Extract a math problem from raw image bytes using GPT-4o Vision.

    Args:
        image_bytes: Raw bytes of a JPG or PNG image.

    Returns:
        {
            "extracted_text": str,
            "confidence": float (0.0–1.0),
            "notes": str,
        }
    """
    client = openai.OpenAI(api_key=config.OPENAI_API_KEY)

    try:
        mime = _detect_mime_type(image_bytes)
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        data_url = f"data:{mime};base64,{b64}"

        prompt = (
            "Extract the math problem from this image exactly as written. "
            "If the image contains handwritten text, do your best to interpret it.\n\n"
            "Return JSON only:\n"
            "{\n"
            '  "extracted_text": "the math problem as text",\n'
            '  "confidence": 0.0-1.0,\n'
            '  "notes": "any issues with readability"\n'
            "}"
        )

        response = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                }
            ],
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content or "{}"
        result = json.loads(content)

        return {
            "extracted_text": result.get("extracted_text", ""),
            "confidence": float(result.get("confidence", 0.5)),
            "notes": result.get("notes", ""),
        }

    except Exception as e:
        return {
            "extracted_text": "",
            "confidence": 0.0,
            "notes": f"OCR failed: {e}",
        }
