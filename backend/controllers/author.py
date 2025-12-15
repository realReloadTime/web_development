from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse

from backend.service.author import get_author_service
from backend.schemas.author import AuthorFull, AuthorDefault
from backend.security.authorization import get_current_user

router = APIRouter(prefix='/authors', tags=['author'])


@router.get('', response_model=list[AuthorFull])
async def get_authors(request: Request):
    service = await get_author_service()
    return await service.get_author()


@router.get('/{author_id}', response_model=AuthorFull)
async def get_author(request: Request, author_id: int):
    service = await get_author_service()
    result = await service.get_author(author_id)
    if result is None:
        return JSONResponse({"error": "Author was not found"}, status_code=404)
    return result


@router.post('', response_model=AuthorFull)
async def create_author(request: Request, author: AuthorDefault,
                        current_user = Depends(get_current_user)):
    service = await get_author_service()
    try:
        return await service.create_author(author)
    except ValueError as ve:
        return JSONResponse({"error": str(ve)}, status_code=400)
    except AttributeError as ae:
        return JSONResponse({"error": str(ae)}, status_code=400)


@router.put('/{author_id}', response_model=AuthorFull)
async def update_author(request: Request, author_id: int, author: AuthorDefault,
                        current_user = Depends(get_current_user)):
    service = await get_author_service()
    try:
        return await service.update_author(author_id, author)
    except ValueError as ve:
        return JSONResponse({"error": str(ve)}, status_code=404)
    except AttributeError as ae:
        return JSONResponse({"error": str(ae)}, status_code=400)


@router.delete('/{author_id}', status_code=204)
async def delete_author(request: Request, author_id: int,
                        current_user = Depends(get_current_user)):
    service = await get_author_service()
    await service.delete_author(author_id)