"""Validated, structured output returned by the Board2Learn vision pipeline."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field, field_validator


class KeyTerm(BaseModel):
    term: str
    meaning_bn: str


class CodeSnippet(BaseModel):
    title: str = "Extracted code"
    language: str = "text"
    code: str


class Flashcard(BaseModel):
    question: str
    answer: str


class QuizQuestion(BaseModel):
    question: str
    options: list[str] = Field(min_length=2, max_length=5)
    correct_answer: str

    @field_validator("correct_answer")
    @classmethod
    def answer_must_be_an_option(cls, value: str, info) -> str:
        options = info.data.get("options", [])
        if options and value not in options:
            raise ValueError("correct_answer must match one of the options")
        return value


class StudyGuide(BaseModel):
    title: str
    detected_languages: list[str] = Field(min_length=1)
    clean_notes_markdown: str
    bangla_explanation: str
    key_terms: list[KeyTerm] = Field(default_factory=list)
    code_snippets: list[CodeSnippet] = Field(default_factory=list)
    flashcards: list[Flashcard] = Field(default_factory=list, max_length=10)
    quiz: list[QuizQuestion] = Field(default_factory=list, max_length=5)
    unclear_sections: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)

    def to_markdown(self) -> str:
        content = [f"# {self.title}", self.clean_notes_markdown, "## সহজ বাংলা", self.bangla_explanation]
        if self.key_terms:
            content += ["## Key Terms", *[f"- **{term.term}** — {term.meaning_bn}" for term in self.key_terms]]
        if self.code_snippets:
            content.append("## Code Snippets")
            content.extend(f"### {item.title}\n```{item.language}\n{item.code}\n```" for item in self.code_snippets)
        if self.flashcards:
            content.append("## Flashcards")
            content.extend(f"- **Q:** {card.question}\n  **A:** {card.answer}" for card in self.flashcards)
        if self.quiz:
            content.append("## Quiz")
            content.extend(f"- {item.question}\n  উত্তর: {item.correct_answer}" for item in self.quiz)
        if self.unclear_sections:
            content += ["## Unclear Sections", *[f"- {item}" for item in self.unclear_sections]]
        output = Path("board2learn_study_guide.md")
        output.write_text("\n\n".join(content), encoding="utf-8")
        return str(output)
