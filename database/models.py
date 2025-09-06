from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Optional

from database.engine import Base, uniq_str, text_t, text_tnn


class User(Base):
    username: Mapped[Optional[str]]
    password_hash: Mapped[str]
    email: Mapped[str]


class Book(Base):
    title: Mapped[str]
    author: Mapped[int] = mapped_column(ForeignKey('authors.id'))
    publication_year: Mapped[Optional[int]]
    genre: Mapped[Optional[int]] = mapped_column(ForeignKey('genres.id'))
    isbn: Mapped[Optional[str]]  # международный стандартный номер книги
    page_count: Mapped[int]


class Author(Base):
    first_name: Mapped[str]
    second_name: Mapped[str]
    third_name: Mapped[Optional[str]]
    birth_date: Mapped[Optional[datetime]]


class Genre(Base):
    name: Mapped[str]