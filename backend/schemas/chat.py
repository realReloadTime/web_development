from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class ChatRoomBase(BaseModel):
    name: Optional[str] = None
    is_group: bool = False


class ChatRoomCreate(ChatRoomBase):
    participant_ids: List[int] = []


class ChatRoomResponse(ChatRoomBase):
    id: int
    created_at: datetime
    participant_count: int

    class Config:
        from_attributes = True


class ChatParticipantBase(BaseModel):
    room_id: int
    user_id: int
    is_admin: bool = False


class ChatParticipantResponse(ChatParticipantBase):
    id: int
    joined_at: datetime
    username: Optional[str] = None
    email: str

    class Config:
        from_attributes = True


class ChatMessageBase(BaseModel):
    content: str
    room_id: int
    message_type: str = "text"


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessageResponse(ChatMessageBase):
    id: int
    sender_id: int
    created_at: datetime
    is_read: bool
    sender_username: Optional[str] = None

    class Config:
        from_attributes = True


class WebSocketMessage(BaseModel):
    """Схема для вебсокет сообщений"""
    type: str  # message, join, leave, typing, read_receipt
    room_id: int
    sender_id: int
    data: dict
    timestamp: datetime = datetime.now()


class JoinRoomRequest(BaseModel):
    room_id: int
    user_id: int
