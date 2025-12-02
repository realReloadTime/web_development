from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from backend.database.engine import get_async_session
from backend.database.models import Author


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


async def get_author_repository() -> AuthorRepository:
    return AuthorRepository()
