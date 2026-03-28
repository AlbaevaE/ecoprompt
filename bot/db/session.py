from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from bot.config import settings
from bot.db.models import Base


def _make_async_url(url: str) -> str:
    """Convert postgresql:// to postgresql+asyncpg:// automatically."""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


_url = _make_async_url(settings.database_url)
_is_pooler = "pooler.supabase.com" in _url

engine = create_async_engine(
    _url,
    echo=False,
    # Supabase transaction pooler doesn't support prepared statements
    **({"connect_args": {"statement_cache_size": 0, "prepared_statement_cache_size": 0}} if _is_pooler else {}),
)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        return session
