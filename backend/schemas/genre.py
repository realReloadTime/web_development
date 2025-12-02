from pydantic import BaseModel, ConfigDict


class GenreDefault(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)


class GenreFull(GenreDefault):
    id: int | None = None
