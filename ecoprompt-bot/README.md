# EcoPrompt Bot

A Telegram bot that teaches Kyrgyz and Russian-speaking students to write efficient AI prompts while understanding their environmental impact.

Every interaction with a large language model costs electricity and water. EcoPrompt helps students learn to communicate with AI concisely and effectively — saving tokens, saving resources, and building better prompting habits.

## Why This Exists

AI usage is growing fast, but most users waste tokens with filler words, vague instructions, and unnecessarily long prompts. In Central Asia, where digital literacy education around AI is still developing, there is an opportunity to teach good habits early.

EcoPrompt addresses this by:

- **Teaching prompt engineering** through a structured 9-lesson curriculum available in Kyrgyz and Russian
- **Quantifying environmental cost** — every practice attempt shows the electricity (Wh) and water (ml) saved by writing a shorter prompt
- **Encouraging ethical AI use** — lessons cover using AI as a learning tool, not a shortcut for cheating
- **Making learning fun** — points, streaks, leaderboards, and daily tips keep students engaged

## Features

- **9 interactive lessons** — from "What are tokens?" to advanced techniques like chain-of-thought and system prompts
- **Practice mode** — real-world tasks (explain photosynthesis, create a study plan, review an essay) scored on quality and efficiency
- **AI feedback** — optional Claude-powered suggestions to improve prompts (3 free per day. Not added yet)
- **Gamification** — earn points, maintain streaks, climb the leaderboard
- **Bilingual** — full support for Kyrgyz and Russian

## Tech Stack

| Component | Technology |
|-----------|------------|
| Bot framework | [aiogram](https://github.com/aiogram/aiogram) 3.x (async) |
| Database | PostgreSQL via SQLAlchemy 2.0 + asyncpg |
| LLM (optional) | Anthropic Claude API |
| Token counting | tiktoken |
| Scheduling | APScheduler |
| Deployment | Docker, Railway |

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL database (or [Supabase](https://supabase.com))
- Telegram bot token from [@BotFather](https://t.me/BotFather)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/ecoprompt-bot.git
   cd ecoprompt-bot
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

3. Copy the example environment file and fill in your values:
   ```bash
   cp .env.example .env
   ```

   | Variable | Required | Description |
   |----------|----------|-------------|
   | `BOT_TOKEN` | Yes | Telegram bot token |
   | `DATABASE_URL` | Yes | PostgreSQL connection string |
   | `ANTHROPIC_API_KEY` | No | Enables "Get AI feedback" in practice mode |

4. Run the bot:
   ```bash
   python -m bot
   ```

### Docker

```bash
docker compose up --build
```

### Deploy to Railway

The project includes a `railway.json` config. Connect your GitHub repo to [Railway](https://railway.app), set the environment variables, and deploy.

## Project Structure

```
bot/
├── __main__.py           # Entry point
├── config.py             # Settings from .env
├── db/                   # Database models, session, CRUD
├── handlers/             # Telegram command handlers
├── services/             # Business logic (scoring, token counting, LLM)
├── middlewares/           # i18n, rate limiting
├── keyboards/            # Telegram UI buttons
├── i18n/                 # Translation files (ru, ky)
└── content/              # Lessons, practice tasks, quizzes, tips
```

## How Scoring Works

Practice prompts are evaluated using rule-based pattern matching (no AI required):

- **Quality score (0-10)** — base 5.0, adjusted by matched task criteria and filler word penalties
- **Efficiency score (0-1)** — blend of quality (50%) and token savings vs. baseline (50%)
- **Points** — base 5 + criteria bonuses + efficiency bonuses + streak bonus

Environmental impact is calculated at 0.0003 Wh and 0.00017 ml water per token saved.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
