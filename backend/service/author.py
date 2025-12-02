from backend.repository.author import AuthorRepository, get_author_repository
from backend.schemas.author import AuthorFull, AuthorDefault


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
