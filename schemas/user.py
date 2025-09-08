from pydantic import BaseModel


class UserAuth(BaseModel):
    email: str
    password: str


class UserDefault(BaseModel):
    email: str
    password_hash: str


class UserFull(UserDefault):
    id: int | None = None
    username: str | None = None