from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
import asyncio

from app.config import settings
engine = create_async_engine(settings.database_url)


SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase): pass

"""
for testing
"""
async def main():
    async with SessionLocal() as session:
        result = await session.execute(text("SELECT 2.2"))
        print(result.scalar())
        
if __name__ == "__main__":
    asyncio.run(main())