"""Rule-based prompt evaluator — no AI API needed."""

import re

from bot.services.token_counter import count_tokens

# Filler words/phrases to penalize (Russian and English)
FILLER_PATTERNS_RU = [
    r"\bпожалуйста\b",
    r"\bне мог бы ты\b",
    r"\bне могли бы вы\b",
    r"\bбудьте добры\b",
    r"\bбыло бы здорово\b",
    r"\bмне нужно чтобы\b",
    r"\bя хочу чтобы ты\b",
    r"\bя хотел бы\b",
    r"\bпомоги мне\b",
]

FILLER_PATTERNS_EN = [
    r"\bplease\b",
    r"\bcould you\b",
    r"\bwould you\b",
    r"\bcan you\b",
    r"\bi want you to\b",
    r"\bi need you to\b",
    r"\bi would like\b",
    r"\bit would be great\b",
    r"\bhelp me\b",
]

# Ethics red flags — prompts asking AI to do work instead of teaching
ETHICS_RED_FLAGS_RU = [
    r"напиши\s+(мне\s+)?(эссе|сочинение|реферат|курсовую|домашнюю|диплом)",
    r"сделай\s+(мне\s+)?(домашн|задани|работу)",
    r"реши\s+(мне\s+)?(задач|пример|уравнен)",
    r"напиши\s+код\s+(для|за\s+меня)",
    r"сделай\s+за\s+меня",
    r"ответь\s+на\s+(вопрос|тест|экзамен)",
    r"напиши\s+ответ",
]

ETHICS_RED_FLAGS_EN = [
    r"write\s+(my|an?|the)\s+(essay|paper|homework|assignment|thesis|report)",
    r"do\s+my\s+(homework|assignment|work|project)",
    r"solve\s+(this|my|the)\s+(problem|equation|exercise)",
    r"write\s+(the\s+)?code\s+for\s+me",
    r"answer\s+(this|my|the)\s+(question|test|exam|quiz)",
    r"give\s+me\s+the\s+answer",
]


def _count_filler(text: str) -> int:
    text_lower = text.lower()
    count = 0
    for pattern in FILLER_PATTERNS_RU + FILLER_PATTERNS_EN:
        count += len(re.findall(pattern, text_lower))
    return count


def check_ethics(text: str) -> bool:
    """Returns True if the prompt has ethics red flags (asking AI to do work)."""
    text_lower = text.lower()
    for pattern in ETHICS_RED_FLAGS_RU + ETHICS_RED_FLAGS_EN:
        if re.search(pattern, text_lower):
            return True
    return False


def evaluate_prompt(text: str, task: dict) -> dict:
    """
    Evaluate a user's prompt against a practice task.

    task should have: criteria (list of dicts with 'pattern' and 'points'),
    baseline_tokens, max_points.
    """
    token_count = count_tokens(text)
    baseline = task["baseline_tokens"]
    tokens_saved = max(0, baseline - token_count)

    # Start with base quality score
    quality = 5.0
    points = 5  # base points for attempting

    # Check each criterion from the task
    criteria_met = 0
    criteria_total = len(task.get("criteria", []))
    for criterion in task.get("criteria", []):
        pattern = criterion["pattern"]
        if re.search(pattern, text, re.IGNORECASE):
            criteria_met += 1
            quality += criterion.get("quality_boost", 0.5)
            points += criterion.get("points", 2)

    # Penalize filler words
    filler_count = _count_filler(text)
    quality -= filler_count * 0.3
    points -= filler_count

    # Bonus for token efficiency
    if baseline > 0:
        savings_pct = (tokens_saved / baseline) * 100
        if savings_pct >= 75 and quality >= 8:
            points += 20
        elif savings_pct >= 50 and quality >= 7:
            points += 10
        elif savings_pct >= 25:
            points += 5
    else:
        savings_pct = 0.0

    # Clamp values
    quality = max(0.0, min(10.0, quality))
    points = max(0, points)

    # Efficiency is a blend of quality and token savings
    efficiency = (quality / 10) * 0.5 + (min(savings_pct, 100) / 100) * 0.5

    has_ethics_issue = check_ethics(text)

    return {
        "token_count": token_count,
        "baseline_tokens": baseline,
        "tokens_saved": tokens_saved,
        "savings_pct": round(savings_pct, 1),
        "quality_score": round(quality, 1),
        "efficiency_score": round(efficiency, 2),
        "points_earned": points,
        "filler_count": filler_count,
        "criteria_met": criteria_met,
        "criteria_total": criteria_total,
        "has_ethics_issue": has_ethics_issue,
    }
