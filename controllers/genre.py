from fastapi import APIRouter
from fastapi.requests import Request

from logic.genre import get_genre_service, GenreService
from schemas.genre import GenreFull, GenreDefault

router = APIRouter(prefix='/genres')


@router.get('', response_model=list[GenreFull])
async def get_genres(request: Request):
    service = await get_genre_service()
    return await service.get_genre()


@router.get('/{genre_id}', response_model=GenreFull)
async def get_genre(request: Request, genre_id: int):
    service = await get_genre_service()
    return await service.get_genre(genre_id)


@router.post('/{genre_id}', response_model=GenreFull)
async def create_genre(request: Request, genre: GenreDefault):
    service = await get_genre_service()
    return await service.create_genre(genre)


@router.put('/{genre_id}', response_model=GenreFull)
async def update_genre(request: Request, genre_id: int, genre: GenreDefault):
    service = await get_genre_service()
    return await service.update_genre(genre_id, genre)


@router.delete('/{genre_id}', status_code=204)
async def delete_genre(request: Request, genre_id: int):
    service = await get_genre_service()
    await service.delete_genre(genre_id)