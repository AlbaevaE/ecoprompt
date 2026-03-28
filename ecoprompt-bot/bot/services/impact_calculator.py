from bot.services.token_counter import tokens_to_ml_water, tokens_to_wh


def format_impact(tokens_saved: int, lang: str = "ru") -> str:
    wh = tokens_to_wh(tokens_saved)
    ml = tokens_to_ml_water(tokens_saved)
    wh_1k = round(wh * 1000, 2)
    ml_1k = round(ml * 1000, 2)
    return {
        "wh": f"{wh:.4f}",
        "ml": f"{ml:.4f}",
        "wh_1k": f"{wh_1k:.2f}",
        "ml_1k": f"{ml_1k:.2f}",
    }
