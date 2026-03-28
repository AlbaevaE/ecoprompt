POINTS_LESSON_COMPLETE = 10
POINTS_QUIZ_PERFECT = 5
POINTS_PRACTICE_BASE = 5
POINTS_STREAK_BONUS = 5  # per day for 3+ day streak


def streak_bonus(streak_days: int) -> int:
    if streak_days >= 3:
        return POINTS_STREAK_BONUS
    return 0
