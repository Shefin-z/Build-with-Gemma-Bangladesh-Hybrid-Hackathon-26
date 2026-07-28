"""Board2Learn BD Gradio application."""

from __future__ import annotations

import gradio as gr

from gemma_service import analyze_whiteboard
from schemas import StudyGuide
from utils import flashcards_markdown, quiz_markdown


DISCLAIMER = (
    "⚠️ Generated content should be checked against the original board. "
    "অস্পষ্ট হাতের লেখা বা ছবির glare থাকলে ফল ভুল হতে পারে।"
)


def render_result(image) -> tuple[str, str, str, str, str, str, str, str, str]:
    if image is None:
        message = "প্রথমে একটি whiteboard বা note-এর ছবি upload করুন।"
        return (message, "", "", "", "", "", "", "")

    result: StudyGuide = analyze_whiteboard(image)
    languages = ", ".join(result.detected_languages)
    status = (
        f"### {result.title}\n"
        f"ভাষা: **{languages}** · Confidence: **{result.confidence:.0%}**\n\n{DISCLAIMER}"
    )
    key_terms = "\n".join(
        f"- **{term.term}** — {term.meaning_bn}" for term in result.key_terms
    ) or "কোনো key term আলাদা করে পাওয়া যায়নি।"
    code = "\n\n".join(
        f"### {snippet.title}\n```{snippet.language}\n{snippet.code}\n```"
        for snippet in result.code_snippets
    ) or "কোনো code বা pseudocode পাওয়া যায়নি।"
    unclear = "\n".join(f"- {item}" for item in result.unclear_sections) or "কোনো অস্পষ্ট অংশ চিহ্নিত হয়নি।"
    markdown_file = result.to_markdown()
    return (
        status,
        result.clean_notes_markdown,
        result.bangla_explanation,
        key_terms,
        code,
        flashcards_markdown(result),
        quiz_markdown(result),
        unclear,
        markdown_file,
    )


with gr.Blocks(title="Board2Learn BD") as demo:
    gr.Markdown(
        "# Board2Learn BD\n"
        "### Whiteboard to Interactive Bangla Study Guide\n"
        "Bangla-English whiteboard বা handwritten note upload করুন—Gemma Vision সেটিকে clean notes, সহজ বাংলা explanation, flashcards ও quiz-এ রূপান্তর করবে।"
    )

    with gr.Row():
        with gr.Column(scale=1):
            source_image = gr.Image(
                label="Whiteboard / Note Image", type="pil", sources=["upload", "webcam"]
            )
            generate = gr.Button("✨ Generate Study Guide", variant="primary", size="lg")
            gr.Markdown("ছবিটি JPG, PNG বা WEBP হতে পারে। পরিষ্কার, সোজা এবং আলোযুক্ত ছবি সবচেয়ে ভালো ফল দেয়।")
        with gr.Column(scale=2):
            status = gr.Markdown("ছবি upload করে Generate Study Guide চাপুন।")
            with gr.Tabs():
                with gr.Tab("Clean Notes"):
                    clean_notes = gr.Markdown()
                with gr.Tab("সহজ বাংলা"):
                    bangla_explanation = gr.Markdown()
                with gr.Tab("Key Terms"):
                    key_terms = gr.Markdown()
                with gr.Tab("Code Snippets"):
                    code_snippets = gr.Markdown()
                with gr.Tab("Flashcards"):
                    flashcards = gr.Markdown()
                with gr.Tab("Quiz"):
                    quiz = gr.Markdown()
                with gr.Tab("Unclear Sections"):
                    unclear = gr.Markdown()
            download = gr.File(label="Download Markdown Study Guide")

    generate.click(
        render_result,
        inputs=source_image,
        outputs=[status, clean_notes, bangla_explanation, key_terms, code_snippets, flashcards, quiz, unclear, download],
    )
    gr.Markdown("---\n" + DISCLAIMER)


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", theme=gr.themes.Soft())
