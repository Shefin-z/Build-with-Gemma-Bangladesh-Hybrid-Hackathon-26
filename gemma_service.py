"""Vision gateway with JSON validation for Gemma or Google-hosted models."""

from __future__ import annotations

import base64
import json
import os
import re
from typing import Any
from urllib.parse import urlparse

import httpx
from dotenv import load_dotenv
from PIL import Image
from pydantic import ValidationError

from prompt import SYSTEM_PROMPT
from schemas import StudyGuide
from utils import preprocess_image

load_dotenv()

class VisionServiceNotConfigured(RuntimeError):
    """Raised when no authorised vision provider has been configured."""


def _extract_json(raw: str) -> dict[str, Any]:
    cleaned = raw.strip().removeprefix("```json").removesuffix("```").strip()
    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if not match:
        raise ValueError("Gemma did not return a JSON object")
    return json.loads(match.group(0))


def _normalise_result(result: dict[str, Any]) -> dict[str, Any]:
    """Make a best-effort model response safe for the strict UI schema.

    Vision models can return an empty language list for a nearly blank image,
    or use the singular field name from an older Board2Learn prompt.  Those
    minor omissions should not discard otherwise useful extracted notes.
    """
    if not isinstance(result, dict):
        raise ValueError("Vision model did not return a JSON object")

    languages = result.get("detected_languages", result.get("detected_language", []))
    if isinstance(languages, str):
        languages = [languages]
    if not isinstance(languages, list):
        languages = []

    confidence = result.get("confidence", 0.0)
    try:
        confidence = min(1.0, max(0.0, float(confidence)))
    except (TypeError, ValueError):
        confidence = 0.0

    normalised = dict(result)
    normalised["title"] = str(result.get("title") or result.get("topic") or "Extracted study guide")
    normalised["detected_languages"] = [str(item) for item in languages if str(item).strip()] or ["Unknown"]
    normalised["clean_notes_markdown"] = str(
        result.get("clean_notes_markdown") or result.get("clean_notes") or "No readable text was extracted."
    )
    normalised["bangla_explanation"] = str(
        result.get("bangla_explanation") or result.get("summary_bn") or "পড়ার মতো স্পষ্ট লেখা পাওয়া যায়নি।"
    )
    normalised["confidence"] = confidence
    for field in ("key_terms", "code_snippets", "flashcards", "quiz", "unclear_sections"):
        if not isinstance(normalised.get(field), list):
            normalised[field] = []
    return normalised


def _call_remote_openai_compatible(image_bytes: bytes) -> dict[str, Any]:
    endpoint, api_key = os.getenv("GEMMA_API_URL"), os.getenv("GEMMA_API_KEY")
    if not endpoint or not api_key:
        raise VisionServiceNotConfigured("GEMMA_API_URL and GEMMA_API_KEY are not configured")
    payload = {
        "model": os.getenv("GEMMA_MODEL", "gemma-3-4b-it"),
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": SYSTEM_PROMPT},
            {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + base64.b64encode(image_bytes).decode("ascii")}},
        ]}],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }
    response = httpx.post(endpoint, headers={"Authorization": f"Bearer {api_key}"}, json=payload, timeout=120)
    response.raise_for_status()
    payload = response.json()
    content = payload.get("choices", [{}])[0].get("message", {}).get("content", payload)
    return _extract_json(content if isinstance(content, str) else json.dumps(content))


def _call_google_vision(image_bytes: bytes, endpoint: str | None = None) -> dict[str, Any]:
    """Optional Google AI Studio route for users who have a Google API key.

    A Gemma-compatible endpoint remains the preferred project route. This path is
    provided so a student can run real image analysis immediately with a Google
    Vision-capable model when that is the key they already have.
    """
    # Google AI Studio API keys are API keys, not OAuth bearer tokens.  The
    # generateContent endpoint accepts them through the x-goog-api-key header
    # (or a `key` query parameter).  Sending one as `Authorization: Bearer`
    # produces a 401 even when the key itself is valid.
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMMA_API_KEY")
    model = os.getenv("GOOGLE_VISION_MODEL", "gemini-2.5-flash")
    if endpoint:
        url = endpoint
        if "{model}" in url:
            url = url.format(model=model)
        elif url.endswith("/"):
            url = f"{url}models/{model}:generateContent"
        elif ":generateContent" not in url:
            url = f"{url.rstrip('/')}/models/{model}:generateContent"
        headers = {"x-goog-api-key": api_key} if api_key else {}
    else:
        if not api_key:
            raise VisionServiceNotConfigured("No Google API key is configured")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        headers = {}
    payload = {
        "contents": [{"role": "user", "parts": [
            {"text": SYSTEM_PROMPT},
            {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(image_bytes).decode("ascii")}},
        ]}],
        "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"},
    }
    response = httpx.post(url, json=payload, headers=headers, timeout=120)
    response.raise_for_status()
    response_body = response.json()
    content = response_body["candidates"][0]["content"]["parts"][0]["text"]
    return _extract_json(content)


def _not_configured_guide() -> StudyGuide:
    return StudyGuide(
        title="Vision model not configured",
        detected_languages=["Unknown"],
        clean_notes_markdown=(
            "## ছবিটি এখনও analyse করা হয়নি\n\n"
            "এই app-এ এখন কোনো authorised Gemma Vision endpoint বা Google Vision API key নেই। "
            "তাই ভুল sample note দেখানোর বদলে analysis বন্ধ রাখা হয়েছে।"
        ),
        bangla_explanation=(
            "`.env` file-এ `GEMMA_API_URL` ও `GEMMA_API_KEY` দিন। বিকল্পভাবে "
            "`GOOGLE_API_KEY` এবং `GOOGLE_VISION_MODEL` দিলে Google Vision route ব্যবহার হবে।"
        ),
        unclear_sections=["Vision provider configuration required before image text can be read."],
        confidence=0,
    )


def analyze_whiteboard(image: Image.Image) -> StudyGuide:
    """Preprocess image → Gemma Vision → Pydantic-validated study guide."""
    try:
        image_bytes = preprocess_image(image)
        gemma_api_url = os.getenv("GEMMA_API_URL")
        gemma_api_key = os.getenv("GEMMA_API_KEY")
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if gemma_api_url and gemma_api_key:
            parsed = urlparse(gemma_api_url)
            if "generateContent" in gemma_api_url or "generativelanguage.googleapis.com" in parsed.netloc:
                result = _call_google_vision(image_bytes, gemma_api_url)
            else:
                result = _call_remote_openai_compatible(image_bytes)
        elif google_api_key:
            result = _call_google_vision(image_bytes)
        else:
            result = _call_google_vision(image_bytes)
        return StudyGuide.model_validate(_normalise_result(result))
    except VisionServiceNotConfigured:
        return _not_configured_guide()
    except (httpx.HTTPError, ValueError, json.JSONDecodeError, ValidationError) as error:
        return StudyGuide(
            title="Image analysis failed",
            detected_languages=["Unknown"],
            clean_notes_markdown="## ছবির লেখা পড়া যায়নি\n\nপরিষ্কার, সোজা ছবি দিয়ে আবার চেষ্টা করুন।",
            bangla_explanation="Vision provider-এর response validate করা যায়নি; কোনো content তৈরি করা হয়নি।",
            unclear_sections=[f"Analysis error: {error}"],
            confidence=0,
        )
