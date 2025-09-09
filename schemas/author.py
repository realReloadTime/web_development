from pydantic import BaseModel, ConfigDict
from datetime import datetime

class AuthorDefault(BaseModel):
    first_name: str
    second_name: str

    model_config = ConfigDict(from_attributes=True)


class AuthorFull(AuthorDefault):
    id: int | None = None
    third_name: str | None = None
    birth_date: datetime | None = None