from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: str
    database_url: str = "postgresql+asyncpg://postgres:YOUR_PASSWORD@db.YOUR_PROJECT.supabase.co:5432/postgres"
    anthropic_api_key: str = ""  # Optional: only for "Get AI feedback"
    ai_feedback_daily_limit: int = 3
    daily_tip_hour: int = 9  # 9:00 AM Bishkek time (UTC+6)
    daily_tip_tz: str = "Asia/Bishkek"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()  # type: ignore[call-arg]
