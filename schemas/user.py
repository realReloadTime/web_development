from pydantic import BaseModel, ConfigDict


class UserAuth(BaseModel):
    email: str
    password: str


class UserDefault(BaseModel):
    email: str
    password_hash: str

    model_config = ConfigDict(from_attributes=True)


class UserFull(UserDefault):
    id: int | None = None
    username: str | None = None