from backend.repository.genre import GenreRepository, get_genre_repository
from backend.schemas.genre import GenreFull, GenreDefault


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
