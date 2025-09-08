from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from database.engine import get_async_session
from database.models import Author
from schemas.author import AuthorFull, AuthorDefault


class AuthorRepository:
    @staticmethod
    async def create_author(**fields) -> Author | None:
        if 'id' in fields: del fields['id']

        async with get_async_session() as session:
            new_author = Author(**fields)
            try:
                await session.add(Author)
                await session.flush()
                new_author = await session.execute(select(Author).where(Author.id == new_author.id))
            except IntegrityError as error:
                raise ValueError(f'Error on author creation: {str(error)}')
        return new_author


    @staticmethod
    async def get_author(author_id: int) -> Author | None:
        async with get_async_session(False) as session:
            author = await session.execute(select(Author).where(Author.id == author_id))
            return author.scalar_one_or_none()


    @staticmethod
    async def update_author(author_id: int, **fields) -> Author | None:
        if 'id' in fields: del fields['id']

        async with get_async_session() as session:
            author = await session.execute(select(Author).where(Author.id == author_id))
            author = author.scalar_one_or_none()
            if author is not None:
                for field, value in fields.items():
                    setattr(author, field, value)
            else:
                raise ValueError('Error on author update - author not found')
            await session.flush()
            author = await session.execute(select(Author).where(Author.id == author_id))
        return author


    @staticmethod
    async def delete_author(author_id: int) -> bool:
        async with get_async_session() as session:
            author = await session.execute(select(Author).where(Author.id == author_id))
            author = author.scalar_one_or_none()
            if author is not None:
                await session.delete(author)
                return True
        return False


class AuthorService:
    def __init__(self, author_repository: AuthorRepository):
        self.repository = author_repository

    async def create_author(self, data: AuthorFull | AuthorDefault) -> AuthorFull:
        result = await self.repository.create_author(**data.model_dump())
        serialized = AuthorFull.model_validate(result)
        return serialized

    async def get_author(self, author_id: int) -> AuthorFull | None:
        result = await self.repository.get_author(author_id)
        if result is None:
            return None
        serialized = AuthorFull.model_validate(result)
        return serialized

    async def update_author(self, author_id: int, data: AuthorFull) -> AuthorFull:
        result = await self.repository.update_author(author_id, **data.model_dump())
        serialized = AuthorFull.model_validate(result)
        return serialized

    async def delete_author(self, author_id: int) -> bool:
        result = await self.repository.delete_author(author_id)
        return result
