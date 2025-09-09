from fastapi import APIRouter, Form
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from logic.genre import get_genre_service
from schemas.genre import GenreFull, GenreDefault

router = APIRouter(prefix='/genres')


@router.get('', response_model=list[GenreFull])
async def get_genres(request: Request):
    service = await get_genre_service()
    return await service.get_genre()


@router.get('/{genre_id}', response_model=GenreFull)
async def get_genre(request: Request, genre_id: int):
    service = await get_genre_service()
    result = await service.get_genre(genre_id)
    if result is None:
        return JSONResponse({"error": "Genre was not found"}, status_code=404)
    return result


@router.post('/{genre_id}', response_model=GenreFull)
async def create_genre(request: Request, name: str = Form(...)):
    genre = GenreDefault(name=name)
    service = await get_genre_service()
    try:
        return await service.create_genre(genre)
    except AttributeError as ae:
        return JSONResponse({"error": str(ae)}, status_code=400)


@router.put('/{genre_id}', response_model=GenreFull)
async def update_genre(request: Request, genre_id: int, genre: GenreDefault):
    service = await get_genre_service()
    try:
        return await service.update_genre(genre_id, genre)
    except ValueError as ve:
        return JSONResponse({"error": str(ve)}, status_code=404)
    except AttributeError as ae:
        return JSONResponse({"error": str(ae)}, status_code=400)


@router.delete('/{genre_id}', status_code=204)
async def delete_genre(request: Request, genre_id: int):
    service = await get_genre_service()
    await service.delete_genre(genre_id)
