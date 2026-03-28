"""Optional AI feedback via Claude API — used ONLY for the 'Get AI feedback' button."""

import anthropic

from bot.config import settings


async def get_ai_feedback(user_prompt: str, task_description: str, lang: str) -> str | None:
    if not settings.anthropic_api_key:
        return None

    lang_instruction = "Отвечай на русском языке." if lang == "ru" else "Кыргыз тилинде жооп бер."

    try:
        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        response = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            system=(
                "You are a prompt engineering tutor for students. "
                "Give brief, actionable feedback on how to improve the student's prompt. "
                "Focus on: conciseness, clarity, specificity, and token efficiency. "
                f"{lang_instruction}"
            ),
            messages=[{
                "role": "user",
                "content": (
                    f"Task: {task_description}\n\n"
                    f"Student's prompt:\n{user_prompt}\n\n"
                    "Give 2-3 specific suggestions to make this prompt shorter and better."
                ),
            }],
        )
        return response.content[0].text
    except Exception:
        return None
