from pydantic import BaseModel
from datetime import datetime

class AuthorDefault(BaseModel):
    first_name: str
    second_name: str


class AuthorFull(AuthorDefault):
    id: int | None = None
    third_name: str | None = None
    birth_date: datetime | None = None