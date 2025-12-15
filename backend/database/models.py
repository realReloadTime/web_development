from sqlalchemy import ForeignKey, DateTime, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
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


class ChatRoom(Base):
    """Комната чата"""
    name: Mapped[str | None]  # Название комнаты (для групповых чатов)
    is_group: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    # Отношения
    participants = relationship("ChatParticipant", back_populates="room", cascade="all, delete-orphan")
    messages = relationship("ChatMessage", back_populates="room", cascade="all, delete-orphan")

    def __str__(self):
        if self.is_group:
            return f"Group Chat: {self.name or f'Room {self.id}'}"
        return f"Private Chat: Room {self.id}"


class ChatParticipant(Base):
    """Участник чата"""
    room_id: Mapped[int] = mapped_column(ForeignKey('chatrooms.id', ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete="CASCADE"))
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    is_admin: Mapped[bool] = mapped_column(default=False)

    # Отношения
    room = relationship("ChatRoom", back_populates="participants", lazy="selectin")
    user = relationship("User", lazy="selectin")

    def __str__(self):
        return f"Participant {self.user_id} in Room {self.room_id}"


class ChatMessage(Base):
    """Сообщение в чате"""
    room_id: Mapped[int] = mapped_column(ForeignKey('chatrooms.id', ondelete="CASCADE"))
    sender_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete="CASCADE"))
    content: Mapped[str] = mapped_column(Text)
    message_type: Mapped[str] = mapped_column(default="text")  # text, image, file, system
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    is_read: Mapped[bool] = mapped_column(default=False)

    # Отношения
    room = relationship("ChatRoom", back_populates="messages")
    sender = relationship("User")

    def __str__(self):
        return f"Message {self.id} from {self.sender_id} in {self.room_id}"
