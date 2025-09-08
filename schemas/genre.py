from pydantic import BaseModel


class GenreDefault(BaseModel):
    name: str


class GenreFull(GenreDefault):
    id: int | None = None