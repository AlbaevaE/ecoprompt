FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --no-cache-dir .

COPY bot/ ./bot/

# DATABASE_URL is set via .env (Supabase PostgreSQL)

CMD ["python", "-m", "bot"]
