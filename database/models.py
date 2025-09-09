from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from database.engine import Base, uniq_str, text_t, text_tnn


class User(Base):
    username: Mapped[str | None]
    password_hash: Mapped[str]
    email: Mapped[str]


class Book(Base):
    title: Mapped[str]
    author: Mapped[int] = mapped_column(ForeignKey('authors.id'))
    publication_year: Mapped[int | None]
    genre: Mapped[int | None] = mapped_column(ForeignKey('genres.id'))
    isbn: Mapped[str | None]  # международный стандартный номер книги
    page_count: Mapped[int | None]
    reserved_by: Mapped[int | None] = mapped_column(ForeignKey('users.id'))


class Author(Base):
    first_name: Mapped[str]
    second_name: Mapped[str]
    third_name: Mapped[str | None]
    birth_date: Mapped[datetime | None]


class Genre(Base):
    name: Mapped[uniq_str]