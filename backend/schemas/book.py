from pydantic import BaseModel, ConfigDict


class BookDefault(BaseModel):
    title: str
    author: int
    genre: int | None = None

    model_config = ConfigDict(from_attributes=True)


class BookFull(BookDefault):
    id: int | None = None
    publication_year: int | None = None
    isbn: str | None = None
    page_count: int | None = None
    reserved_by: int | None = None
