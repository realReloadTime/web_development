from sqlalchemy import ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from backend.database.engine import Base, uniq_str


class User(Base):
    username: Mapped[str | None]
    password_hash: Mapped[str]
    email: Mapped[str]

    def __str__(self):
        return self.username if self.username else self.email


class Book(Base):
    title: Mapped[str]
    author: Mapped[int] = mapped_column(ForeignKey('authors.id'))
    publication_year: Mapped[int | None]
    genre: Mapped[int | None] = mapped_column(ForeignKey('genres.id'))
    isbn: Mapped[str | None]  # международный стандартный номер книги
    page_count: Mapped[int | None]
    reserved_by: Mapped[int | None] = mapped_column(ForeignKey('users.id'))

    def __str__(self):
        return f'{self.title} - {self.isbn if self.isbn else 'NO ISBN'}'


class Author(Base):
    first_name: Mapped[str]
    second_name: Mapped[str]
    third_name: Mapped[str | None]
    birth_date: Mapped[datetime | None]

    def __str__(self):
        return f'{self.first_name} {self.second_name}{' ' + self.third_name if self.third_name else ''}{' д.р.: ' + self.birth_date.isoformat() if self.birth_date else ''}'


class Genre(Base):
    name: Mapped[uniq_str]

    def __str__(self):
        return f'{self.name}'


class Booking(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    book_id: Mapped[int] = mapped_column(ForeignKey('books.id'))

    take_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
