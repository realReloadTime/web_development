from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from database.engine import get_async_session
from database.models import Book
from schemas.book import BookFull, BookDefault


class BookRepository:
    @staticmethod
    async def create_book(**fields) -> Book | None:
        if 'id' in fields: del fields['id']

        async with get_async_session() as session:
            new_book = Book(**fields)
            try:
                await session.add(Book)
                await session.flush()
                new_book = await session.execute(select(Book).where(Book.id == new_book.id))
            except IntegrityError as error:
                raise ValueError(f'Error on book creation: {str(error)}')
        return new_book


    @staticmethod
    async def get_book(book_id: int) -> Book | None:
        async with get_async_session(False) as session:
            book = await session.execute(select(Book).where(Book.id == book_id))
            return book.scalar_one_or_none()


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
            book = await session.execute(select(Book).where(Book.id == book_id))
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


class BookService:
    def __init__(self, book_repository: BookRepository):
        self.repository = book_repository

    async def create_book(self, data: BookFull | BookDefault) -> BookFull:
        result = await self.repository.create_book(**data.model_dump())
        serialized = BookFull.model_validate(result)
        return serialized

    async def get_book(self, book_id: int) -> BookFull | None:
        result = await self.repository.get_book(book_id)
        if result is None:
            return None
        serialized = BookFull.model_validate(result)
        return serialized

    async def update_book(self, book_id: int, data: BookFull) -> BookFull:
        result = await self.repository.update_book(book_id, **data.model_dump())
        serialized = BookFull.model_validate(result)
        return serialized

    async def delete_book(self, book_id: int) -> bool:
        result = await self.repository.delete_book(book_id)
        return result
