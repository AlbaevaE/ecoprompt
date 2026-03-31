import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import settings
from bot.db.session import init_db
from bot.handlers import feedback, lessons, practice, resources, settings as settings_handler, start, tips, tracker
from bot.middlewares.i18n import I18nMiddleware, load_translations
from bot.middlewares.throttle import ThrottleMiddleware
from bot.services.lesson_engine import load_quizzes
from bot.handlers.practice import load_tasks
from bot.handlers.tips import load_tips

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    # Init
    await init_db()
    load_translations()
    load_quizzes()
    load_tasks()
    load_tips()

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    # Register middleware
    dp.message.middleware(ThrottleMiddleware())
    dp.message.middleware(I18nMiddleware())
    dp.callback_query.middleware(I18nMiddleware())

    # Register routers
    dp.include_router(start.router)
    dp.include_router(lessons.router)
    dp.include_router(practice.router)
    dp.include_router(tracker.router)
    dp.include_router(tips.router)
    dp.include_router(resources.router)
    dp.include_router(feedback.router)
    dp.include_router(settings_handler.router)

    logger.info("EcoPrompt bot starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
