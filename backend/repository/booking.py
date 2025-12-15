from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from backend.database.engine import get_async_session
from backend.database.models import Booking, Book


class BookingRepository:
    @staticmethod
    async def create_booking(**fields) -> Booking | None:
        if 'id' in fields:
            del fields['id']

        async with get_async_session() as session:
            # Проверяем, доступна ли книга
            book = await session.execute(
                select(Book).where(Book.id == fields['book_id'])
            )
            book = book.scalar_one_or_none()

            if not book:
                raise ValueError('Book not found')

            if book.reserved_by is not None:
                raise ValueError('Book is already reserved')

            new_booking = Booking(**fields)
            try:
                # Резервируем книгу
                book.reserved_by = fields['user_id']
                session.add(new_booking)
                await session.flush()
                await session.refresh(new_booking)
            except IntegrityError as error:
                raise ValueError(f'Error on booking creation: {str(error)}')
        return new_booking

    @staticmethod
    async def get_booking(booking_id: int | None = None, user_id: int | None = None) -> Booking | list[Booking] | None:
        async with get_async_session(False) as session:
            if booking_id is not None:
                booking = await session.execute(
                    select(Booking).where(Booking.id == booking_id)
                )
                return booking.scalar_one_or_none()
            elif user_id is not None:
                bookings = await session.execute(
                    select(Booking).where(Booking.user_id == user_id)
                )
                return bookings.scalars().all()
            else:
                bookings = await session.execute(select(Booking))
                return bookings.scalars().all()

    @staticmethod
    async def update_booking(booking_id: int, **fields) -> Booking | None:
        if 'id' in fields:
            del fields['id']

        async with get_async_session() as session:
            booking = await session.execute(
                select(Booking).where(Booking.id == booking_id)
            )
            booking = booking.scalar_one_or_none()

            if booking is not None:
                for field, value in fields.items():
                    setattr(booking, field, value)
            else:
                raise ValueError('Error on booking update - booking not found')

            await session.flush()
            await session.refresh(booking)
        return booking

    @staticmethod
    async def delete_booking(booking_id: int) -> bool:
        async with get_async_session() as session:
            booking = await session.execute(
                select(Booking).where(Booking.id == booking_id)
            )
            booking = booking.scalar_one_or_none()

            if booking is not None:
                # Освобождаем книгу при удалении бронирования
                book = await session.execute(
                    select(Book).where(Book.id == booking.book_id)
                )
                book = book.scalar_one_or_none()
                if book:
                    book.reserved_by = None

                await session.delete(booking)
                return True
        return False

    @staticmethod
    async def complete_booking(booking_id: int) -> Booking | None:
        """Завершение бронирования (возврат книги)"""
        async with get_async_session() as session:
            booking = await session.execute(
                select(Booking).where(Booking.id == booking_id)
            )
            booking = booking.scalar_one_or_none()

            if booking is None:
                raise ValueError('Booking not found')

            if booking.end_date is not None:
                raise ValueError('Booking already completed')

            # Устанавливаем дату возврата
            from datetime import datetime
            booking.end_date = datetime.now()

            # Освобождаем книгу
            book = await session.execute(
                select(Book).where(Book.id == booking.book_id)
            )
            book = book.scalar_one_or_none()
            if book:
                book.reserved_by = None

            await session.flush()
            await session.refresh(booking)
            return booking


async def get_booking_repository() -> BookingRepository:
    return BookingRepository()
