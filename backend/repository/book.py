from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from backend.database.engine import get_async_session
from backend.database.models import Book


class BookRepository:
    @staticmethod
    async def create_book(**fields) -> Book | None:
        if 'id' in fields: del fields['id']

        async with get_async_session() as session:
            new_book = Book(**fields)
            try:
                session.add(new_book)
                await session.flush()
                await session.refresh(new_book)
            except IntegrityError as error:
                raise ValueError(f'Error on book creation: {str(error)}')
        return new_book


    @staticmethod
    async def get_book(book_id: int | None) -> Book | list[Book] | None:
        async with get_async_session(False) as session:
            if book_id is not None:
                book = await session.execute(select(Book).where(Book.id == book_id))
                return book.scalar_one_or_none()
            else:
                books = await session.execute(select(Book))
                return books.scalars().all()


    @staticmethod
    async def update_book(book_id: int, **fields) -> Book | None:
        if 'id' in fields: del fields['id']

        async with get_async_session() as session:
            book = await session.execute(select(Book).where(Book.id == book_id))
            book = book.scalar_one_or_none()
            if book is not None:
                for field, value in fields.items():
                    setattr(book, field, value)
            else:
                raise ValueError('Error on book update - book not found')
            await session.flush()
            await session.refresh(book)
        return book


    @staticmethod
    async def delete_book(book_id: int) -> bool:
        async with get_async_session() as session:
            book = await session.execute(select(Book).where(Book.id == book_id))
            book = book.scalar_one_or_none()
            if book is not None:
                await session.delete(book)
                return True
        return False


async def get_book_repository() -> BookRepository:
    return BookRepository()