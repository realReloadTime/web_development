from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from backend.database.engine import get_async_session
from backend.database.models import Genre


class GenreRepository:
    async def create_genre(self, **fields) -> Genre | None:
        if 'id' in fields: del fields['id']

        async with get_async_session() as session:
            await self._check_name_unique(session, fields['name'])
            new_genre = Genre(**fields)
            try:
                session.add(new_genre)
                await session.flush()
                await session.refresh(new_genre)
            except IntegrityError as error:
                raise ValueError(f'Error on genre creation: {str(error)}')
        return new_genre

    @staticmethod
    async def get_genre(genre_id: int | None) -> Genre | list[Genre] | None:
        async with get_async_session(False) as session:
            if genre_id is not None:
                genre = await session.execute(select(Genre).where(Genre.id == genre_id))
                return genre.scalar_one_or_none()
            else:
                genres = await session.execute(select(Genre))
                return genres.scalars().all()

    async def update_genre(self, genre_id: int, **fields) -> Genre | None:
        if 'id' in fields: del fields['id']

        async with get_async_session() as session:
            await self._check_name_unique(session, fields['name'], genre_id)
            genre = await session.execute(select(Genre).where(Genre.id == genre_id))
            genre = genre.scalar_one_or_none()
            if genre is not None:
                for field, value in fields.items():
                    setattr(genre, field, value)
            else:
                raise ValueError('Error on genre update - genre not found')
            await session.flush()
            await session.refresh(genre)
        return genre

    @staticmethod
    async def delete_genre(genre_id: int) -> bool:
        async with get_async_session() as session:
            genre = await session.execute(select(Genre).where(Genre.id == genre_id))
            genre = genre.scalar_one_or_none()
            if genre is not None:
                await session.delete(genre)
                return True
        return False

    @staticmethod
    async def _check_name_unique(session, name, exclude_genre_id=None):
        query = select(Genre).where(Genre.name == name)
        if exclude_genre_id is not None:
            query = query.where(Genre.id != exclude_genre_id)
        result = await session.execute(query)
        if result.scalar_one_or_none() is not None:
            raise AttributeError(f"Genre with name '{name}' already exists")


async def get_genre_repository() -> GenreRepository:
    return GenreRepository()
