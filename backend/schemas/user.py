from pydantic import BaseModel, ConfigDict


class UserRegister(BaseModel):
    email: str
    password: str
    password_confirm: str


class UserDefault(BaseModel):
    email: str

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    username: str

    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserDefault):
    id: int | None = None
    username: str | None = None
