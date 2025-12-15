from sqlalchemy import select, or_, and_
from sqlalchemy.orm import joinedload, selectinload
from typing import List, Optional

from backend.database.engine import get_async_session
from backend.database.models import ChatRoom, ChatParticipant, ChatMessage, User


class ChatRepository:
    @staticmethod
    async def create_chat_room(name: Optional[str] = None, is_group: bool = False) -> ChatRoom:
        """Создать новую комнату чата"""
        async with get_async_session() as session:
            room = ChatRoom(name=name, is_group=is_group)
            session.add(room)
            await session.flush()
            await session.refresh(room)
            return room

    @staticmethod
    async def add_participant(room_id: int, user_id: int, is_admin: bool = False) -> ChatParticipant:
        """Добавить участника в комнату"""
        async with get_async_session() as session:
            # Проверяем, не является ли пользователь уже участником
            existing = await session.execute(
                select(ChatParticipant).where(
                    and_(ChatParticipant.room_id == room_id, ChatParticipant.user_id == user_id)
                )
            )
            if existing.scalar_one_or_none():
                raise ValueError("User is already a participant in this room")

            participant = ChatParticipant(
                room_id=room_id,
                user_id=user_id,
                is_admin=is_admin
            )
            session.add(participant)
            await session.flush()
            await session.refresh(participant)
            return participant

    @staticmethod
    async def create_private_chat(user1_id: int, user2_id: int) -> ChatRoom:
        """Создать приватный чат между двумя пользователями"""
        async with get_async_session() as session:
            # Проверяем, существует ли уже приватный чат
            existing_room = await session.execute(
                select(ChatRoom).join(ChatParticipant).where(
                    and_(
                        ChatRoom.is_group == False,
                        or_(
                            and_(
                                ChatParticipant.user_id == user1_id,
                                ChatRoom.id.in_(
                                    select(ChatParticipant.room_id).where(ChatParticipant.user_id == user2_id)
                                )
                            ),
                            and_(
                                ChatParticipant.user_id == user2_id,
                                ChatRoom.id.in_(
                                    select(ChatParticipant.room_id).where(ChatParticipant.user_id == user1_id)
                                )
                            )
                        )
                    )
                ).distinct()
            )

            existing_room = existing_room.scalar_one_or_none()
            if existing_room:
                return existing_room

            # Создаем новую комнату
            room = ChatRoom(is_group=False)
            session.add(room)
            await session.flush()

            # Добавляем участников
            participant1 = ChatParticipant(room_id=room.id, user_id=user1_id)
            participant2 = ChatParticipant(room_id=room.id, user_id=user2_id)
            session.add_all([participant1, participant2])
            await session.flush()
            await session.refresh(room)
            return room

    @staticmethod
    async def create_group_chat(name: str, creator_id: int, participant_ids: List[int]) -> ChatRoom:
        """Создать групповой чат"""
        async with get_async_session() as session:
            room = ChatRoom(name=name, is_group=True)
            session.add(room)
            await session.flush()

            # Добавляем создателя как администратора
            participants = [ChatParticipant(
                room_id=room.id,
                user_id=creator_id,
                is_admin=True
            )]

            # Добавляем остальных участников
            for user_id in participant_ids:
                if user_id != creator_id:
                    participants.append(ChatParticipant(
                        room_id=room.id,
                        user_id=user_id,
                        is_admin=False
                    ))

            session.add_all(participants)
            await session.flush()
            await session.refresh(room)
            return room

    @staticmethod
    async def get_user_chat_rooms(user_id: int) -> List[ChatRoom]:
        """Получить все чаты пользователя"""
        async with get_async_session(commit=False) as session:
            result = await session.execute(
                select(ChatRoom)
                .join(ChatParticipant)
                .where(ChatParticipant.user_id == user_id)
                .options(
                    joinedload(ChatRoom.participants).joinedload(ChatParticipant.user)
                    # Загружаем участников и их пользователей
                )
            )
            rooms = result.unique().scalars().all()
            return rooms

    @staticmethod
    async def get_chat_room(room_id: int, user_id: Optional[int] = None) -> Optional[ChatRoom]:
        """Получить комнату чата по ID с проверкой доступа"""
        async with get_async_session(commit=False) as session:
            query = select(ChatRoom).where(ChatRoom.id == room_id)

            if user_id:
                query = query.join(ChatParticipant).where(ChatParticipant.user_id == user_id)

            result = await session.execute(query)
            return result.scalar_one_or_none()

    @staticmethod
    async def get_room_participants(room_id: int) -> List[ChatParticipant]:
        """Получить всех участников комнаты"""
        async with get_async_session(commit=False) as session:
            result = await session.execute(
                select(ChatParticipant)
                .where(ChatParticipant.room_id == room_id)
                .options(joinedload(ChatParticipant.user))  # Важно: загружаем связанного пользователя
            )
            participants = result.unique().scalars().all()
            return participants

    @staticmethod
    async def save_message(room_id: int, sender_id: int, content: str, message_type: str = "text") -> ChatMessage:
        """Сохранить сообщение в базе данных"""
        async with get_async_session() as session:
            # Проверяем, является ли отправитель участником чата
            participant = await session.execute(
                select(ChatParticipant).where(
                    and_(ChatParticipant.room_id == room_id, ChatParticipant.user_id == sender_id)
                )
            )

            if not participant.scalar_one_or_none():
                raise ValueError("Sender is not a participant in this chat room")

            # Создаем сообщение
            message = ChatMessage(
                room_id=room_id,
                sender_id=sender_id,
                content=content,
                message_type=message_type
            )

            # Добавляем сообщение
            session.add(message)
            await session.flush()
            await session.refresh(message)

            # Загружаем отправителя
            await session.refresh(message, ['sender'])

            return message

    @staticmethod
    async def get_room_messages(room_id: int, limit: int = 50, offset: int = 0) -> List[ChatMessage]:
        """Получить сообщения комнаты с пагинацией"""
        async with get_async_session(commit=False) as session:
            result = await session.execute(
                select(ChatMessage)
                .where(ChatMessage.room_id == room_id)
                .order_by(ChatMessage.created_at.desc())
                .limit(limit)
                .offset(offset)
                .options(joinedload(ChatMessage.sender))  # Загружаем отправителя
            )
            messages = result.unique().scalars().all()
            return messages

    @staticmethod
    async def mark_messages_as_read(room_id: int, user_id: int) -> int:
        """Пометить все непрочитанные сообщения в комнате как прочитанные для пользователя"""
        async with get_async_session() as session:
            # Получаем все сообщения, которые отправили не мы и которые еще не прочитаны
            result = await session.execute(
                select(ChatMessage).where(
                    and_(
                        ChatMessage.room_id == room_id,
                        ChatMessage.sender_id != user_id,
                        ChatMessage.is_read == False
                    )
                )
            )
            messages = result.scalars().all()

            for message in messages:
                message.is_read = True

            await session.flush()
            return len(messages)

    @staticmethod
    async def get_message_with_sender(message_id: int) -> Optional[ChatMessage]:
        """Получить сообщение с информацией об отправителе"""
        async with get_async_session(commit=False) as session:
            result = await session.execute(
                select(ChatMessage)
                .options(joinedload(ChatMessage.sender))
                .where(ChatMessage.id == message_id)
            )
            return result.unique().scalar_one_or_none()

    @staticmethod
    async def mark_message_as_read(message_id: int, user_id: int) -> bool:
        """Пометить конкретное сообщение как прочитанное"""
        async with get_async_session() as session:
            try:
                result = await session.execute(
                    select(ChatMessage)
                    .where(
                        and_(
                            ChatMessage.id == message_id,
                            ChatMessage.sender_id != user_id,
                            ChatMessage.is_read == False
                        )
                    )
                )
                message = result.scalar_one_or_none()

                if message:
                    message.is_read = True
                    await session.flush()
                    return True
                return False
            except Exception as e:
                print(f"Error marking message as read: {e}")
                return False

    @staticmethod
    async def remove_participant(room_id: int, user_id: int) -> bool:
        """Удалить участника из комнаты"""
        async with get_async_session() as session:
            participant = await session.execute(
                select(ChatParticipant).where(
                    and_(ChatParticipant.room_id == room_id, ChatParticipant.user_id == user_id)
                )
            )
            participant = participant.scalar_one_or_none()

            if participant:
                await session.delete(participant)
                return True
            return False

    @staticmethod
    async def delete_chat_room(room_id: int) -> bool:
        """Удалить комнату чата"""
        async with get_async_session() as session:
            room = await session.execute(select(ChatRoom).where(ChatRoom.id == room_id))
            room = room.scalar_one_or_none()

            if room:
                await session.delete(room)
                return True
            return False

    @staticmethod
    async def get_unread_count(user_id: int, room_id: Optional[int] = None) -> int:
        """Получить количество непрочитанных сообщений"""
        async with get_async_session(commit=False) as session:
            # Создаем явный JOIN с указанием условия
            query = (
                select(ChatMessage)
                .select_from(ChatMessage)
                .join(
                    ChatParticipant,
                    and_(
                        ChatMessage.room_id == ChatParticipant.room_id,
                        ChatParticipant.user_id == user_id
                    )
                )
                .where(
                    and_(
                        ChatMessage.sender_id != user_id,
                        ChatMessage.is_read == False
                    )
                )
            )

            if room_id:
                query = query.where(ChatMessage.room_id == room_id)

            result = await session.execute(query)
            messages = result.scalars().all()
            return len(messages)

async def get_chat_repository() -> ChatRepository:
    return ChatRepository()
