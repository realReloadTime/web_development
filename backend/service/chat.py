from typing import List, Optional
from backend.repository.chat import ChatRepository, get_chat_repository
from backend.schemas.chat import (
    ChatRoomCreate, ChatRoomResponse, ChatMessageCreate,
    ChatMessageResponse, ChatParticipantResponse
)


class ChatService:
    def __init__(self, chat_repository: ChatRepository):
        self.repository = chat_repository

    async def create_private_chat(self, user1_id: int, user2_id: int) -> ChatRoomResponse:
        """Создать приватный чат между двумя пользователями"""
        room = await self.repository.create_private_chat(user1_id, user2_id)
        participants = await self.repository.get_room_participants(room.id)

        response = ChatRoomResponse(
            id=room.id,
            name=room.name,
            is_group=room.is_group,
            created_at=room.created_at,
            participant_count=len(participants)
        )
        return response

    async def create_group_chat(self, name: str, creator_id: int, participant_ids: List[int]) -> ChatRoomResponse:
        """Создать групповой чат"""
        room = await self.repository.create_group_chat(name, creator_id, participant_ids)
        participants = await self.repository.get_room_participants(room.id)

        response = ChatRoomResponse(
            id=room.id,
            name=room.name,
            is_group=room.is_group,
            created_at=room.created_at,
            participant_count=len(participants)
        )
        return response

    async def get_user_chats(self, user_id: int) -> List[ChatRoomResponse]:
        """Получить все чаты пользователя"""
        rooms = await self.repository.get_user_chat_rooms(user_id)

        result = []
        for room in rooms:
            participants = await self.repository.get_room_participants(room.id)
            unread_count = await self.repository.get_unread_count(user_id, room.id)

            chat_response = ChatRoomResponse(
                id=room.id,
                name=room.name,
                is_group=room.is_group,
                created_at=room.created_at,
                participant_count=len(participants)
            )
            # Добавим дополнительное поле для непрочитанных сообщений
            chat_response.__dict__['unread_count'] = unread_count
            result.append(chat_response)

        return result

    async def get_chat_messages(self, room_id: int, user_id: int, limit: int = 50, offset: int = 0) -> List[
        ChatMessageResponse]:
        """Получить сообщения чата"""
        # Проверяем доступ пользователя к чату
        room = await self.repository.get_chat_room(room_id, user_id)
        if not room:
            raise ValueError("Chat room not found or access denied")

        messages = await self.repository.get_room_messages(room_id, limit, offset)

        # Помечаем сообщения как прочитанные
        await self.repository.mark_messages_as_read(room_id, user_id)

        result = []
        for message in messages:
            response = ChatMessageResponse(
                id=message.id,
                room_id=message.room_id,
                sender_id=message.sender_id,
                content=message.content,
                message_type=message.message_type,
                created_at=message.created_at,
                is_read=message.is_read,
                sender_username=message.sender.username if message.sender else None
            )
            result.append(response)

        return result

    async def send_message(self, room_id: int, sender_id: int, content: str,
                           message_type: str = "text") -> ChatMessageResponse:
        """Отправить сообщение"""
        message = await self.repository.save_message(room_id, sender_id, content, message_type)

        response = ChatMessageResponse(
            id=message.id,
            room_id=message.room_id,
            sender_id=message.sender_id,
            content=message.content,
            message_type=message.message_type,
            created_at=message.created_at,
            is_read=message.is_read,
            sender_username=message.sender.username if message.sender else None
        )
        return response

    async def get_room_participants(self, room_id: int, user_id: int) -> List[ChatParticipantResponse]:
        """Получить участников комнаты"""
        room = await self.repository.get_chat_room(room_id, user_id)
        if not room:
            raise ValueError("Chat room not found or access denied")

        participants = await self.repository.get_room_participants(room_id)

        result = []
        for participant in participants:
            response = ChatParticipantResponse(
                id=participant.id,
                room_id=participant.room_id,
                user_id=participant.user_id,
                is_admin=participant.is_admin,
                joined_at=participant.joined_at,
                username=participant.user.username,
                email=participant.user.email
            )
            result.append(response)

        return result

    async def add_participant_to_group(self, room_id: int, admin_id: int, user_id: int) -> bool:
        """Добавить участника в групповой чат"""
        room = await self.repository.get_chat_room(room_id, admin_id)
        if not room:
            raise ValueError("Chat room not found or access denied")

        if not room.is_group:
            raise ValueError("Can only add participants to group chats")

        # Проверяем, является ли пользователь администратором
        participants = await self.repository.get_room_participants(room_id)
        admin_participant = next((p for p in participants if p.user_id == admin_id and p.is_admin), None)
        if not admin_participant:
            raise ValueError("Only admins can add participants")

        await self.repository.add_participant(room_id, user_id)
        return True

    async def remove_participant(self, room_id: int, admin_id: int, user_id: int) -> bool:
        """Удалить участника из чата"""
        room = await self.repository.get_chat_room(room_id, admin_id)
        if not room:
            raise ValueError("Chat room not found or access denied")

        # Проверяем права администратора (для групповых чатов)
        if room.is_group:
            participants = await self.repository.get_room_participants(room_id)
            admin_participant = next((p for p in participants if p.user_id == admin_id and p.is_admin), None)
            if not admin_participant:
                raise ValueError("Only admins can remove participants")

        return await self.repository.remove_participant(room_id, user_id)

    async def get_unread_count(self, user_id: int, room_id: Optional[int] = None) -> int:
        """Получить количество непрочитанных сообщений"""
        return await self.repository.get_unread_count(user_id, room_id)


async def get_chat_service() -> ChatService:
    return ChatService(await get_chat_repository())
