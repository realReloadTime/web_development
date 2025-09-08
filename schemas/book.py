from pydantic import BaseModel


class BookDefault(BaseModel):
    title: str
    author: int


class BookFull(BookDefault):
    id: int | None = None
    publication_year: int | None = None
    isbn: str | None = None
    page_count: int | None = None
    reserved_by: int | None = None