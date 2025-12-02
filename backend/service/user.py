from backend.repository.user import UserRepository
from backend.schemas.user import UserRegister, UserUpdate, UserResponse
from backend.schemas.token import TokenPair
from backend.security.authorization import get_password_hash, verify_password, create_access_token, create_refresh_token


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def create_user(self, user: UserRegister) -> UserResponse:
        if user.password != user.password_confirm:
            raise ValueError('Passwords do not match')
        if await self.user_repository.get_user_by_email(str(user.email)) is not None:
            raise AttributeError('Email already registered')
        hashed_password = get_password_hash(user.password)
        user = await self.user_repository.register_user(email=user.email, password_hash=hashed_password)
        if user is not None:
            return UserResponse.model_validate(user)
        raise MemoryError('User not registered')

    async def login_user(self, email, password) -> TokenPair:
        email_user = await self.user_repository.get_user_by_email(email)
        if email_user is None or not verify_password(password, email_user.password_hash):
            raise AttributeError('Invalid email or password')
        access_token = create_access_token({"sub": email_user.email})
        if await self.user_repository.user_access(email_user.id):
            return TokenPair.model_validate({
                "access_token": access_token,
                "refresh_token": create_refresh_token({"sub": email_user.email}),
                "token_type": "bearer"
            })
        raise ValueError('User not logged in')

    async def get_all(self) -> list[UserResponse]:
        return [UserResponse.model_validate(user) for user in await self.user_repository.get_all_users()]

    async def update_user(self, user_id, new_user_data: UserUpdate) -> UserResponse:
        new_user = await self.user_repository.update_user(user_id=user_id,
                                                          **new_user_data.model_dump(exclude_unset=True))
        return UserResponse.model_validate(new_user)

    async def delete_user(self, user_id) -> bool:
        return await self.user_repository.delete_user(user_id=user_id)


async def get_user_service() -> UserService:
    return UserService(UserRepository())
