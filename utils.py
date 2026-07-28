"""Image preparation and presentational helpers."""

from __future__ import annotations

from io import BytesIO

from PIL import Image, ImageOps

from schemas import StudyGuide


def preprocess_image(image: Image.Image, max_dimension: int = 1600) -> bytes:
    """Fix phone-image orientation and compress it for slow connections/model input."""
    prepared = ImageOps.exif_transpose(image).convert("RGB")
    prepared.thumbnail((max_dimension, max_dimension))
    buffer = BytesIO()
    prepared.save(buffer, format="JPEG", quality=85, optimize=True)
    return buffer.getvalue()


def flashcards_markdown(result: StudyGuide) -> str:
    if not result.flashcards:
        return "Flashcard তৈরি করার মতো পর্যাপ্ত readable content পাওয়া যায়নি।"
    return "\n\n".join(f"### কার্ড {index}\n**প্রশ্ন:** {item.question}\n\n**উত্তর:** ||{item.answer}||" for index, item in enumerate(result.flashcards, 1))


def quiz_markdown(result: StudyGuide) -> str:
    if not result.quiz:
        return "Quiz তৈরি করার মতো পর্যাপ্ত readable content পাওয়া যায়নি।"
    cards = []
    for index, item in enumerate(result.quiz, 1):
        options = "\n".join(f"- {option}" for option in item.options)
        cards.append(f"### প্রশ্ন {index}\n{item.question}\n\n{options}\n\n**সঠিক উত্তর:** ||{item.correct_answer}||")
    return "\n\n".join(cards)
