from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse

from backend.service.booking import get_booking_service
from backend.schemas.booking import BookingFull, BookingDefault
from backend.security.authorization import get_current_user

router = APIRouter(prefix='/bookings', tags=['booking'])


@router.get('', response_model=list[BookingFull])
async def get_bookings(request: Request, current_user=Depends(get_current_user)):
    service = await get_booking_service()
    # Администраторы видят все бронирования, обычные пользователи - только свои
    if hasattr(current_user, 'is_admin') and current_user.is_admin:
        return await service.get_booking()
    else:
        return await service.get_booking(user_id=current_user.id)


@router.get('/{booking_id}', response_model=BookingFull)
async def get_booking(request: Request, booking_id: int, current_user=Depends(get_current_user)):
    service = await get_booking_service()
    result = await service.get_booking(booking_id)

    if result is None:
        return JSONResponse({"error": "Booking was not found"}, status_code=404)

    # Проверка прав доступа
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        if result.user_id != current_user.id:
            return JSONResponse({"error": "Access denied"}, status_code=403)

    return result


@router.post('', response_model=BookingFull)
async def create_booking(request: Request, booking: BookingDefault,
                         current_user=Depends(get_current_user)):
    # Устанавливаем текущего пользователя как владельца бронирования
    booking.user_id = current_user.id

    service = await get_booking_service()
    try:
        return await service.create_booking(booking)
    except ValueError as ve:
        return JSONResponse({"error": str(ve)}, status_code=400)
    except AttributeError as ae:
        return JSONResponse({"error": str(ae)}, status_code=400)


@router.put('/{booking_id}', response_model=BookingFull)
async def update_booking(request: Request, booking_id: int, booking: BookingDefault,
                         current_user=Depends(get_current_user)):
    service = await get_booking_service()

    # Проверка прав доступа
    existing_booking = await service.get_booking(booking_id)
    if existing_booking and existing_booking.user_id != current_user.id:
        if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
            return JSONResponse({"error": "Access denied"}, status_code=403)

    try:
        return await service.update_booking(booking_id, booking)
    except ValueError as ve:
        return JSONResponse({"error": str(ve)}, status_code=404)
    except AttributeError as ae:
        return JSONResponse({"error": str(ae)}, status_code=400)


@router.delete('/{booking_id}', status_code=204)
async def delete_booking(request: Request, booking_id: int,
                         current_user=Depends(get_current_user)):
    service = await get_booking_service()

    # Проверка прав доступа
    existing_booking = await service.get_booking(booking_id)
    if existing_booking and existing_booking.user_id != current_user.id:
        if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
            return JSONResponse({"error": "Access denied"}, status_code=403)

    await service.delete_booking(booking_id)


@router.post('/{booking_id}/complete', response_model=BookingFull)
async def complete_booking(request: Request, booking_id: int,
                           current_user=Depends(get_current_user)):
    service = await get_booking_service()

    # Проверка прав доступа
    existing_booking = await service.get_booking(booking_id)
    if existing_booking and existing_booking.user_id != current_user.id:
        if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
            return JSONResponse({"error": "Access denied"}, status_code=403)

    try:
        return await service.complete_booking(booking_id)
    except ValueError as ve:
        return JSONResponse({"error": str(ve)}, status_code=400)
