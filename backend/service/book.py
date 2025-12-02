from backend.repository.book import BookRepository, get_book_repository
from backend.schemas.book import BookFull, BookDefault


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
