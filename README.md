# Board2Learn BD

**Whiteboard to Interactive Bangla Study Guide** — a Multimodal Track project for Bangladeshi university students. Upload a Bangla-English whiteboard or handwritten lecture note and receive structured notes, a simple Bangla explanation, key terms, code extraction, flashcards and MCQ quiz questions.

## Core flow

`Image upload → Pillow preprocessing → Gemma Vision → validated JSON → notes, explanation, flashcards and quiz`

Gemma is the core vision component: it reads visible Bangla/English text, separates headings, bullets, diagrams, code and formulas, and returns JSON that is validated with Pydantic before the UI renders it. Unreadable areas are reported instead of guessed.

## Run locally

Requires Python 3.10+.

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

Open the local URL printed by Gradio (normally `http://127.0.0.1:7860`). A real vision provider must be configured before an uploaded image can be read. The app deliberately does **not** show fake sample notes for a real upload.

## Connect Gemma Vision

Put an OpenAI-compatible Gemma Vision endpoint in `.env`; do not commit the file.

```env
GEMMA_API_URL=https://your-provider.example/v1/chat/completions
GEMMA_API_KEY=your_secret_key
GEMMA_MODEL=gemma-3-4b-it
```

The endpoint must support image data URLs and return a chat-completions response. Each response is passed through `StudyGuide` validation; invalid model output falls back safely with an unclear-image warning.

### Alternative Google Vision route

If you have a Google AI Studio key instead, use the following in `.env`. This is an alternative vision provider for local testing; the configured Gemma endpoint takes priority when both are present.

```env
GOOGLE_API_KEY=your_google_ai_studio_key
GOOGLE_VISION_MODEL=gemini-2.5-flash
```

## Project structure

```text
app.py              # Gradio UI with all required result tabs
gemma_service.py    # image → Gemma request → Pydantic validation
prompt.py           # strict JSON-only multimodal prompt
schemas.py           # StudyGuide, flashcard, quiz and code schemas
utils.py             # orientation fix, resize/compression, render helpers
evaluation/          # testing protocol and ground truth location
samples/             # permissioned demo images
notebooks/           # public Kaggle notebook outline
```

## MVP features

- Whiteboard/note image upload with webcam option
- Bangla-English support and low-resolution image preprocessing
- Clean Markdown notes and simple Bangla explanation
- Key terms, code/pseudocode extraction, five flashcards and 3–5 MCQs
- Unclear-section and generated-content warning
- Markdown study-guide download

## Evaluation plan

Test with 30 permissioned/anonymized images: clear Bangla, English, mixed notes, flowcharts, code and difficult low-light photos. Keep ground truth and report only measured text coverage, hallucination rate, structure accuracy, Bangla usefulness and flashcard relevance. Details are in [evaluation/README.md](evaluation/README.md).

## Limitations

Handwriting, glare, cropped content, diagrams and equations can be misread. Generated content must always be checked against the original board. The first MVP intentionally excludes login, database, PDF export and multi-image merging.

## Submission assets to prepare

- Public source repository and deployed Gradio app (for example Hugging Face Spaces)
- Kaggle writeup and public notebook
- Media gallery: upload, processing, original-vs-notes, Bangla explanation, flashcards, quiz, warning, raw JSON and architecture
- 3–5 minute end-to-end demo video
