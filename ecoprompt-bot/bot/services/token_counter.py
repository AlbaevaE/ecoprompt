import tiktoken

_encoding = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    return len(_encoding.encode(text))


# Environmental impact constants (approximate)
WH_PER_TOKEN = 0.0003  # Watt-hours per token
ML_WATER_PER_TOKEN = 0.00017  # millilitres of water per token


def tokens_to_wh(tokens: int) -> float:
    return round(tokens * WH_PER_TOKEN, 4)


def tokens_to_ml_water(tokens: int) -> float:
    return round(tokens * ML_WATER_PER_TOKEN, 4)
