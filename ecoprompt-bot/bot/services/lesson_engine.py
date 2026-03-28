"""Load and manage lesson content from markdown files."""

import json
from pathlib import Path

CONTENT_DIR = Path(__file__).parent.parent / "content"
LESSONS_DIR = CONTENT_DIR / "lessons"

# Lesson registry — order matters
LESSON_SLUGS = [
    "01_what_are_tokens",
    "02_prompt_structure",
    "03_concise_prompting",
    "04_ai_for_learning",
    "05_prompting_to_learn",
    "06_few_shot_roles",
    "07_ai_safety",
    "08_system_prompts",
    "09_advanced_techniques",
]

LESSON_TITLES = {
    "ru": {
        "01_what_are_tokens": "Что такое токены?",
        "02_prompt_structure": "Структура промпта",
        "03_concise_prompting": "Краткость в промптах",
        "04_ai_for_learning": "ИИ для учёбы, а не списывания",
        "05_prompting_to_learn": "Промпты для изучения предмета",
        "06_few_shot_roles": "Few-shot и ролевые промпты",
        "07_ai_safety": "Безопасность ИИ",
        "08_system_prompts": "Системные промпты",
        "09_advanced_techniques": "Продвинутые техники",
    },
    "ky": {
        "01_what_are_tokens": "Токендер деген эмне?",
        "02_prompt_structure": "Промпттун түзүлүшү",
        "03_concise_prompting": "Промптто кыскалык",
        "04_ai_for_learning": "ИИ окуу үчүн, көчүрүү үчүн эмес",
        "05_prompting_to_learn": "Предмет үйрөнүү үчүн промпттор",
        "06_few_shot_roles": "Few-shot жана ролдук промпттор",
        "07_ai_safety": "ИИ коопсуздугу",
        "08_system_prompts": "Системалык промпттор",
        "09_advanced_techniques": "Өнүккөн техникалар",
    },
}

# Quizzes embedded per lesson
QUIZZES: dict[str, list[dict]] = {}

# Max chars per Telegram message chunk
CHUNK_SIZE = 3800


def get_lesson_list(lang: str) -> list[dict]:
    titles = LESSON_TITLES.get(lang, LESSON_TITLES["ru"])
    return [
        {"slug": slug, "title": titles.get(slug, slug)}
        for slug in LESSON_SLUGS
    ]


def load_lesson_content(slug: str, lang: str) -> str | None:
    path = LESSONS_DIR / lang / f"{slug}.md"
    if not path.exists():
        # Fall back to Russian
        path = LESSONS_DIR / "ru" / f"{slug}.md"
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def chunk_lesson(content: str) -> list[str]:
    """Split lesson content into Telegram-friendly chunks."""
    paragraphs = content.split("\n\n")
    chunks = []
    current = ""
    for para in paragraphs:
        if len(current) + len(para) + 2 > CHUNK_SIZE:
            if current:
                chunks.append(current.strip())
            current = para
        else:
            current = current + "\n\n" + para if current else para
    if current.strip():
        chunks.append(current.strip())
    return chunks if chunks else [content[:CHUNK_SIZE]]


def get_quiz(slug: str) -> list[dict] | None:
    return QUIZZES.get(slug)


def load_quizzes() -> None:
    """Load quizzes from the lesson files (JSON block at end) or from registry."""
    quiz_path = CONTENT_DIR / "quizzes.json"
    if quiz_path.exists():
        with open(quiz_path, encoding="utf-8") as f:
            QUIZZES.update(json.load(f))
