from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

import asyncio

from app.database import Base, engine


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    document: Mapped[str]
    page: Mapped[int | None]
    row : Mapped[int | None]
    text: Mapped[str]
    embedding = mapped_column(Vector(384), nullable=False)

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(main())