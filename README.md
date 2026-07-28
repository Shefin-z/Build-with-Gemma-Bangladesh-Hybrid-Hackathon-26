# Board2Learn BD

Board2Learn BD is a multimodal study assistant for Bangladeshi students. Upload a Bangla-English whiteboard or handwritten note and the app uses Gemma Vision to generate structured notes, a simple Bangla explanation, key terms, code extraction, flashcards, and MCQ quizzes.

## Run locally

Create a virtual environment, install the dependencies, copy `.env.example` to `.env`, configure a Gemma Vision endpoint, and run:

```powershell
python app.py
```

The React/Vite frontend can be run with `npm install` followed by `npm run dev`.

Generated content should always be checked against the original note, especially when handwriting, glare, diagrams, or equations are unclear.
