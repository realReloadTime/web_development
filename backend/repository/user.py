from datetime import datetime, UTC

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from backend.database.models import User
from backend.database.engine import get_async_session


class UserRepository:
    async def register_user(self, password_hash, email) -> User | None:
        new_user = User(email=email, password_hash=password_hash)
        async with get_async_session(commit=True) as session:
            try:
                session.add(new_user)
                await session.flush()
                await session.refresh(new_user)
            except IntegrityError as error:
                raise ValueError(f'Error on user creation: {str(error)}')
            return new_user

    async def get_user_by_email(self, email: str) -> User | None:
        async with get_async_session(commit=False) as session:
            result = await session.execute(select(User).where(User.email == email))
            return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> User | None:
        async with get_async_session(commit=False) as session:
            result = await session.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()

    async def get_all_users(self) -> list[User] | None:
        async with get_async_session(commit=False) as session:
            result = await session.execute(select(User).order_by(User.email))
            return result.scalars().all()

    async def update_user(self, user_id: int, **fields) -> User | None:
        async with get_async_session(commit=True) as session:
            user = await session.execute(select(User).where(User.id == user_id))
            user = user.scalar_one_or_none()
            if user is None:
                raise ValueError(f'User not found: {user_id}')
            for field, value in fields.items():
                setattr(user, field, value)
            await session.flush()
            await session.refresh(user)
            return user

    async def delete_user(self, user_id: int) -> bool:
        async with get_async_session(commit=True) as session:
            user = await session.execute(select(User).where(User.id == user_id))
            user = user.scalar_one_or_none()
            if user is None:
                raise ValueError(f'User not found: {user_id}')
            await session.delete(user)
        return True

    async def user_access(self, user_id: int) -> bool:
        async with get_async_session(commit=True) as session:
            user = await session.execute(select(User).where(User.id == user_id))
            user = user.scalar_one_or_none()
            if user is None:
                raise ValueError(f'User not found: {user_id}')
            setattr(user, 'last_login', datetime.now(UTC))
        return True

    async def update_password_by_email(self, email: str, new_password: str) -> User:
        async with get_async_session(commit=True) as session:
            user = await session.execute(select(User).where(User.email == email))
            user = user.scalar_one_or_none()
            if user is None:
                raise ValueError(f'User not found: {email}')
            user.password_hash = new_password
            await session.flush()
            await session.refresh(user)
            return user


async def get_user_repository() -> UserRepository:
    return UserRepository()
