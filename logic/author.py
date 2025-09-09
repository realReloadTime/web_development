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
                session.add(new_author)
                await session.flush()
                await session.refresh(new_author)
            except IntegrityError as error:
                raise ValueError(f'Error on author creation: {str(error)}')
        return new_author


    @staticmethod
    async def get_author(author_id: int | None) -> Author | list[Author] | None:
        async with get_async_session(False) as session:
            if author_id is not None:
                author = await session.execute(select(Author).where(Author.id == author_id))
                return author.scalar_one_or_none()
            else:
                authors = await session.execute(select(Author))
                return authors.scalars().all()


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
            await session.refresh(author)
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
        return AuthorFull.model_validate(result)

    async def get_author(self, author_id: int = None) -> AuthorFull | list[AuthorFull] | None:
        result = await self.repository.get_author(author_id)
        if result is None:
            return None
        if author_id is None:
            return [AuthorFull.model_validate(author) for author in result]
        return AuthorFull.model_validate(result)

    async def update_author(self, author_id: int, data: AuthorFull | AuthorDefault) -> AuthorFull:
        result = await self.repository.update_author(author_id, **data.model_dump())
        return AuthorFull.model_validate(result)

    async def delete_author(self, author_id: int) -> bool:
        return await self.repository.delete_author(author_id)


async def get_author_service() -> AuthorService:
    return AuthorService(await get_author_repository())


async def get_author_repository() -> AuthorRepository:
    return AuthorRepository()