from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from database.engine import get_async_session
from database.models import Genre
from schemas.genre import GenreFull, GenreDefault


class GenreRepository:
    @staticmethod
    async def create_genre(**fields) -> Genre | None:
        if 'id' in fields: del fields['id']

        async with get_async_session() as session:
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


    @staticmethod
    async def update_genre(genre_id: int, **fields) -> Genre | None:
        if 'id' in fields: del fields['id']

        async with get_async_session() as session:
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


class GenreService:
    def __init__(self, genre_repository: GenreRepository):
        self.repository = genre_repository

    async def create_genre(self, data: GenreFull | GenreDefault) -> GenreFull:
        result = await self.repository.create_genre(**data.model_dump())
        return GenreFull.model_validate(result)

    async def get_genre(self, genre_id: int = None) -> GenreFull | list[GenreFull] | None:
        result = await self.repository.get_genre(genre_id)
        if result is None:
            return None
        if genre_id is None:
            return [GenreFull.model_validate(genre) for genre in result]
        return GenreFull.model_validate(result)

    async def update_genre(self, genre_id: int, data: GenreFull | GenreDefault) -> GenreFull:
        result = await self.repository.update_genre(genre_id, **data.model_dump())
        return GenreFull.model_validate(result)

    async def delete_genre(self, genre_id: int) -> bool:
        return await self.repository.delete_genre(genre_id)


async def get_genre_service() -> GenreService:
    return GenreService(await get_genre_repository())


async def get_genre_repository() -> GenreRepository:
    return GenreRepository()