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


class BookService:
    def __init__(self, book_repository: BookRepository):
        self.repository = book_repository

    async def create_book(self, data: BookFull | BookDefault) -> BookFull:
        result = await self.repository.create_book(**data.model_dump())
        return BookFull.model_validate(result)

    async def get_book(self, book_id: int = None) -> BookFull | list[BookFull] | None:
        result = await self.repository.get_book(book_id)
        if result is None:
            return None
        if book_id is None:
            return [BookFull.model_validate(book) for book in result]
        return BookFull.model_validate(result)

    async def update_book(self, book_id: int, data: BookFull | BookDefault) -> BookFull:
        result = await self.repository.update_book(book_id, **data.model_dump())
        return BookFull.model_validate(result)

    async def delete_book(self, book_id: int) -> bool:
        return await self.repository.delete_book(book_id)


async def get_book_service() -> BookService:
    return BookService(await get_book_repository())


async def get_book_repository() -> BookRepository:
    return BookRepository()