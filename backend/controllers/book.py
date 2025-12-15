from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse

from backend.service.book import get_book_service
from backend.schemas.book import BookFull, BookDefault
from backend.security.authorization import get_current_user

router = APIRouter(prefix='/books', tags=['book'])


@router.get('', response_model=list[BookFull])
async def get_books(request: Request):
    service = await get_book_service()
    return await service.get_book()


@router.get('/{book_id}', response_model=BookFull)
async def get_book(request: Request, book_id: int):
    service = await get_book_service()
    result = await service.get_book(book_id)
    if result is None:
        return JSONResponse({"error": "Book was not found"}, status_code=404)
    return result


@router.post('', response_model=BookFull)
async def create_book(request: Request, book: BookDefault,
                      current_user=Depends(get_current_user)):
    service = await get_book_service()
    try:
        return await service.create_book(book)
    except ValueError as ve:
        return JSONResponse({"error": str(ve)}, status_code=400)
    except AttributeError as ae:
        return JSONResponse({"error": str(ae)}, status_code=400)


@router.put('/{book_id}', response_model=BookFull)
async def update_book(request: Request, book_id: int, book: BookDefault,
                      current_user=Depends(get_current_user)):
    service = await get_book_service()
    try:
        return await service.update_book(book_id, book)
    except ValueError as ve:
        return JSONResponse({"error": str(ve)}, status_code=404)
    except AttributeError as ae:
        return JSONResponse({"error": str(ae)}, status_code=400)


@router.delete('/{book_id}', status_code=204)
async def delete_book(request: Request, book_id: int,
                      current_user=Depends(get_current_user)):
    service = await get_book_service()
    await service.delete_book(book_id)
