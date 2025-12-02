from typing import Annotated

from contextlib import asynccontextmanager
from sqlalchemy import Text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapped, declared_attr

from backend.config import Settings

settings = Settings()

engine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=bool(settings.IS_DEBUG),  # логирование SQL-запросов
    future=True  # использование SQLAlchemy API v.2
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)


# ЗДЕСЬ БУДУТ АННОТИРОВАННЫЕ ПОЛЯ
uniq_str = Annotated[str, mapped_column(unique=True)]
text_tnn = Annotated[str, mapped_column(Text, nullable=False)]  # Текстовый тип, не нулевой
text_t = Annotated[str, mapped_column(Text)]  # Просто текстовый тип

# -------------------------------


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'


@asynccontextmanager
async def get_async_session(commit=True):
    """Асинхронный контекстный менеджер для сессий БД, использовать с async with"""
    session = AsyncSessionLocal()
    try:  # автоматическая работа с БД
        yield session  # <- здесь выполняется код тела async with
        if commit:
            await session.commit()  # фиксация изменений при успешном выполнении
    except Exception as e:
        await session.rollback()  # откат при ошибке
        raise e
    finally:
        await session.close()


if __name__ == '__main__':
    import asyncio
    from sqlalchemy.future import select

    async def main():
        async with get_async_session() as session:
            result = await session.execute(select(1))
            print("Simple SELECT test:", result.scalar())


    asyncio.run(main())