from backend.repository.booking import BookingRepository, get_booking_repository
from backend.schemas.booking import BookingFull, BookingDefault


class BookingService:
    def __init__(self, booking_repository: BookingRepository):
        self.repository = booking_repository

    async def create_booking(self, data: BookingFull | BookingDefault) -> BookingFull:
        result = await self.repository.create_booking(**data.model_dump())
        return BookingFull.model_validate(result)

    async def get_booking(self, booking_id: int = None, user_id: int = None) -> BookingFull | list[BookingFull] | None:
        result = await self.repository.get_booking(booking_id, user_id)
        if result is None:
            return None
        if booking_id is None:
            return [BookingFull.model_validate(booking) for booking in result]
        return BookingFull.model_validate(result)

    async def update_booking(self, booking_id: int, data: BookingFull | BookingDefault) -> BookingFull:
        result = await self.repository.update_booking(booking_id, **data.model_dump())
        return BookingFull.model_validate(result)

    async def delete_booking(self, booking_id: int) -> bool:
        return await self.repository.delete_booking(booking_id)

    async def complete_booking(self, booking_id: int) -> BookingFull:
        result = await self.repository.complete_booking(booking_id)
        return BookingFull.model_validate(result)


async def get_booking_service() -> BookingService:
    return BookingService(await get_booking_repository())
