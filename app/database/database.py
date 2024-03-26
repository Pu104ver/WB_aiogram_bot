from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from config import ECHO, settings

engine = create_async_engine(url=settings.database_url_asyncpg, echo=ECHO)
async_session = async_sessionmaker(engine)
