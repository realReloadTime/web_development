from typing import List, Optional, Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends, status
from datetime import datetime
import asyncio

from backend.repository.chat import ChatRepository
from backend.service.chat import get_chat_service, ChatService
from backend.schemas.chat import ChatRoomResponse, ChatMessageResponse, ChatParticipantResponse

router = APIRouter(prefix="/chat", tags=["chat"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[Dict[str, Any]]] = {}

    async def connect(self, websocket: WebSocket, room_id: int, user_id: int):
        await websocket.accept()

        if room_id not in self.active_connections:
            self.active_connections[room_id] = []

        connection_info = {
            "websocket": websocket,
            "user_id": user_id,
            "connected_at": datetime.now()
        }
        self.active_connections[room_id].append(connection_info)

    async def disconnect(self, websocket: WebSocket, room_id: int, user_id: int):
        if room_id in self.active_connections:
            self.active_connections[room_id] = [
                conn for conn in self.active_connections[room_id]
                if conn["websocket"] != websocket
            ]

            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except Exception:
            pass

    async def broadcast(self, room_id: int, message: Dict[str, Any], exclude_user_id: Optional[int] = None):
        if room_id not in self.active_connections:
            return

        disconnected = []
        for connection in self.active_connections[room_id]:
            if exclude_user_id and connection["user_id"] == exclude_user_id:
                continue

            try:
                await connection["websocket"].send_json(message)
            except Exception:
                disconnected.append(connection)

        for connection in disconnected:
            await self.disconnect(connection["websocket"], room_id, connection["user_id"])

    async def notify_typing(self, room_id: int, user_id: int, is_typing: bool):
        typing_message = {
            "type": "typing",
            "room_id": room_id,
            "user_id": user_id,
            "is_typing": is_typing,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast(room_id, typing_message, exclude_user_id=user_id)

    async def notify_message_read(self, room_id: int, user_id: int, message_id: int):
        read_message = {
            "type": "read_receipt",
            "room_id": room_id,
            "user_id": user_id,
            "message_id": message_id,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast(room_id, read_message, exclude_user_id=user_id)


manager = ConnectionManager()


# REST эндпоинты
@router.post("/private/{user2_id}", response_model=ChatRoomResponse)
async def create_private_chat(
        user2_id: int,
        current_user_id: int = 1,
        chat_service: ChatService = Depends(get_chat_service)
):
    """Создать приватный чат с пользователем"""
    return await chat_service.create_private_chat(current_user_id, user2_id)


@router.post("/group", response_model=ChatRoomResponse)
async def create_group_chat(
        name: str,
        participant_ids: List[int],
        current_user_id: int = 1,
        chat_service: ChatService = Depends(get_chat_service)
):
    """Создать групповой чат"""
    return await chat_service.create_group_chat(name, current_user_id, participant_ids)


@router.get("/rooms", response_model=List[ChatRoomResponse])
async def get_my_chat_rooms(
        current_user_id: int = 1,
        chat_service: ChatService = Depends(get_chat_service)
):
    """Получить все мои чаты"""
    return await chat_service.get_user_chats(current_user_id)


@router.get("/rooms/{room_id}/messages", response_model=List[ChatMessageResponse])
async def get_chat_messages(
        room_id: int,
        limit: int = 50,
        offset: int = 0,
        current_user_id: int = 1,
        chat_service: ChatService = Depends(get_chat_service)
):
    """Получить сообщения чата"""
    return await chat_service.get_chat_messages(room_id, current_user_id, limit, offset)


@router.get("/rooms/{room_id}/participants", response_model=List[ChatParticipantResponse])
async def get_chat_participants(
        room_id: int,
        current_user_id: int = 1,
        chat_service: ChatService = Depends(get_chat_service)
):
    """Получить участников чата"""
    return await chat_service.get_room_participants(room_id, current_user_id)


@router.post("/rooms/{room_id}/participants/{user_id}")
async def add_participant(
        room_id: int,
        user_id: int,
        current_user_id: int = 1,
        chat_service: ChatService = Depends(get_chat_service)
):
    """Добавить участника в групповой чат"""
    success = await chat_service.add_participant_to_group(room_id, current_user_id, user_id)
    if success:
        return {"message": "Participant added successfully"}
    raise HTTPException(status_code=400, detail="Failed to add participant")


@router.delete("/rooms/{room_id}/participants/{user_id}")
async def remove_participant(
        room_id: int,
        user_id: int,
        current_user_id: int = 1,
        chat_service: ChatService = Depends(get_chat_service)
):
    """Удалить участника из чата"""
    success = await chat_service.remove_participant(room_id, current_user_id, user_id)
    if success:
        return {"message": "Participant removed successfully"}
    raise HTTPException(status_code=400, detail="Failed to remove participant")


@router.get("/unread")
async def get_unread_count(
        room_id: Optional[int] = None,
        current_user_id: int = 1,
        chat_service: ChatService = Depends(get_chat_service)
):
    """Получить количество непрочитанных сообщений"""
    count = await chat_service.get_unread_count(current_user_id, room_id)
    return {"unread_count": count}


@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
        websocket: WebSocket,
        room_id: int,
        user_id: int = 1
):
    """Вебсокет эндпоинт для чата"""

    await manager.connect(websocket, room_id, user_id)

    try:
        # Используем asyncio.create_task для запуска асинхронной операции
        room_task = asyncio.create_task(ChatRepository.get_chat_room(room_id, user_id))
        room = await room_task

        if not room:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # Основной цикл обработки сообщений
        while True:
            try:
                data = await websocket.receive_json()
                message_type = data.get("type")

                if message_type == "message":
                    content = data.get("content", "").strip()
                    if content:
                        # Создаем задачу для сохранения сообщения
                        save_task = asyncio.create_task(
                            ChatRepository.save_message(room_id, user_id, content)
                        )
                        message = await save_task

                        # Создаем задачу для получения сообщения с отправителем
                        get_message_task = asyncio.create_task(
                            ChatRepository.get_message_with_sender(message.id)
                        )
                        message_with_sender = await get_message_task

                        # Отправляем всем участникам
                        await manager.broadcast(room_id, {
                            "type": "message",
                            "message": {
                                "id": message_with_sender.id,
                                "room_id": message_with_sender.room_id,
                                "sender_id": message_with_sender.sender_id,
                                "content": message_with_sender.content,
                                "message_type": message_with_sender.message_type,
                                "created_at": message_with_sender.created_at.isoformat(),
                                "is_read": message_with_sender.is_read,
                                "sender_username": message_with_sender.sender.username if message_with_sender.sender else None
                            },
                            "timestamp": datetime.now().isoformat()
                        })

                elif message_type == "typing":
                    is_typing = data.get("is_typing", False)
                    await manager.notify_typing(room_id, user_id, is_typing)

                elif message_type == "read":
                    message_id = data.get("message_id")
                    if message_id:
                        # Создаем задачу для асинхронной операции через репозиторий
                        asyncio.create_task(
                            ChatRepository.mark_message_as_read(message_id, user_id)
                        )
                        await manager.notify_message_read(room_id, user_id, message_id)

                elif message_type == "ping":
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }, websocket)

            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"WebSocket processing error: {e}")
                try:
                    await manager.send_personal_message({
                        "type": "error",
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }, websocket)
                except:
                    pass

    except Exception as e:
        print(f"WebSocket connection error: {e}")
    finally:
        await manager.disconnect(websocket, room_id, user_id)


@router.get("/rooms/{room_id}/online")
async def get_online_users(room_id: int):
    """Получить список онлайн пользователей в комнате"""
    if room_id not in manager.active_connections:
        return {"online_users": []}

    online_users = [
        {
            "user_id": conn["user_id"],
            "connected_at": conn["connected_at"].isoformat()
        }
        for conn in manager.active_connections[room_id]
    ]

    return {"online_users": online_users}