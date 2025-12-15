import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useWebSocket } from '../../hooks/useWebSocket';
import { chatService, userService } from '../../services/api';
import './ChatWindow.css';

const ChatWindow = () => {
  const { roomId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [participants, setParticipants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [newMessage, setNewMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  const messagesEndRef = useRef(null);
  const typingTimeoutRef = useRef(null);

  // Создаем ref для хранения markAsRead
  const markAsReadRef = useRef();

  // Обработчик сообщений WebSocket с использованием ref
  const handleWebSocketMessage = useCallback((data) => {
    if (data.type === 'typing') {
      // Типинг обрабатывается в useWebSocket через typingUsers
    } else if (data.type === 'message') {
      // Автоматически отмечаем как прочитанное через ref
      if (markAsReadRef.current) {
        markAsReadRef.current(data.message.id);
      }
    }
  }, []);

  const handleWebSocketError = useCallback((error) => {
    setError(error);
  }, []);

  const {
    isConnected,
    messages,
    typingUsers,
    onlineUsers,
    sendMessage: sendWsMessage,
    sendTypingIndicator,
    markAsRead,
    disconnect
  } = useWebSocket(
    roomId,
    user?.id,
    handleWebSocketMessage,
    handleWebSocketError
  );

  // Обновляем ref при изменении markAsRead
  useEffect(() => {
    markAsReadRef.current = markAsRead;
  }, [markAsRead]);

  useEffect(() => {
    if (roomId && user) {
      loadChatData();
    }
  }, [roomId, user]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Очищаем устаревшие индикаторы набора текста
    const interval = setInterval(() => {
      // Эта логика теперь в useWebSocket
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  // Очистка при размонтировании
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  const loadChatData = async () => {
    try {
      setLoading(true);
      setError('');

      const [participantsData] = await Promise.all([
        chatService.getChatParticipants(roomId)
      ]);

      // Загружаем информацию о пользователях для участников
      const usersInfo = await userService.getAllUsers();
      const participantsWithInfo = participantsData.map(p => ({
        ...p,
        userInfo: usersInfo.find(u => u.id === p.user_id)
      }));
      setParticipants(participantsWithInfo);

    } catch (err) {
      console.error('Failed to load chat data:', err);
      setError('Не удалось загрузить данные чата');
    } finally {
      setLoading(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = (e) => {
    e.preventDefault();

    if (!newMessage.trim()) return;

    if (sendWsMessage(newMessage.trim())) {
      setNewMessage('');
      sendTypingIndicator(false);
      setIsTyping(false);
    } else {
      setError('Не удалось отправить сообщение');
    }
  };

  const handleTyping = () => {
    if (!isTyping) {
      setIsTyping(true);
      sendTypingIndicator(true);
    }

    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }

    typingTimeoutRef.current = setTimeout(() => {
      setIsTyping(false);
      sendTypingIndicator(false);
    }, 3000);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };

  const formatMessageTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('ru-RU', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getUserName = (userId) => {
    const participant = participants.find(p => p.user_id === userId);
    return participant?.userInfo?.username ||
           participant?.userInfo?.email ||
           `Пользователь ${userId}`;
  };

  const isUserOnline = (userId) => {
    return onlineUsers.some(u => u.user_id === userId);
  };

  const getTypingUsers = () => {
    return Object.keys(typingUsers)
      .filter(userId => typingUsers[userId] && userId !== user.id)
      .map(userId => getUserName(userId));
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Загрузка чата...</p>
      </div>
    );
  }

  return (
    <div className="chat-window">
      <header className="chat-header">
        <button
          className="btn-back"
          onClick={() => navigate('/chat')}
        >
          ← Назад
        </button>

        <div className="chat-info">
          <h2>
            {participants.find(p => p.room_id === roomId)?.room?.is_group
              ? (participants.find(p => p.room_id === roomId)?.room?.name || 'Групповой чат')
              : 'Приватный чат'}
          </h2>
          <div className="chat-status">
            <span className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
              {isConnected ? '✓ Онлайн' : '✗ Офлайн'}
            </span>
            <span className="online-count">
              {onlineUsers.length} онлайн
            </span>
          </div>
        </div>
      </header>

      <div className="chat-participants-sidebar">
        <h3>Участники</h3>
        <ul className="participants-list">
          {participants.map(participant => (
            <li key={participant.user_id} className="participant-item">
              <div className="participant-avatar">
                <span>{getUserName(participant.user_id).charAt(0)}</span>
              </div>
              <div className="participant-info">
                <span className="participant-name">
                  {getUserName(participant.user_id)}
                  {participant.user_id === user.id && ' (Вы)'}
                </span>
                <div className="participant-status">
                  <span className={`status-dot ${isUserOnline(participant.user_id) ? 'online' : 'offline'}`} />
                  {isUserOnline(participant.user_id) ? 'Онлайн' : 'Офлайн'}
                  {participant.is_admin && ' 👑'}
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>

      <div className="chat-messages-container">
        <div className="messages-wrapper">
          {messages.length === 0 ? (
            <div className="no-messages">
              <p>Нет сообщений</p>
              <p>Начните общение первым!</p>
            </div>
          ) : (
            messages.map((message, index) => {
              const isOwnMessage = message.sender_id === user.id;
              const showAvatar = index === 0 ||
                messages[index - 1]?.sender_id !== message.sender_id;

              return (
                <div
                  key={message.id}
                  className={`message-wrapper ${isOwnMessage ? 'own-message' : ''}`}
                >
                  {!isOwnMessage && showAvatar && (
                    <div className="message-avatar">
                      <span>{getUserName(message.sender_id).charAt(0)}</span>
                    </div>
                  )}

                  <div className="message-content">
                    {!isOwnMessage && showAvatar && (
                      <div className="message-sender">
                        {getUserName(message.sender_id)}
                      </div>
                    )}

                    <div className="message-bubble">
                      <p>{message.content}</p>
                      <span className="message-time">
                        {formatMessageTime(message.created_at)}
                        {message.is_read && isOwnMessage && ' ✓'}
                      </span>
                    </div>
                  </div>

                  {isOwnMessage && showAvatar && (
                    <div className="message-avatar own">
                      <span>Вы</span>
                    </div>
                  )}
                </div>
              );
            })
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="typing-indicator">
          {getTypingUsers().length > 0 && (
            <p>
              {getTypingUsers().join(', ')}
              {getTypingUsers().length === 1 ? ' печатает...' : ' печатают...'}
            </p>
          )}
        </div>

        <form className="message-input-form" onSubmit={handleSendMessage}>
          <textarea
            value={newMessage}
            onChange={(e) => {
              setNewMessage(e.target.value);
              handleTyping();
            }}
            onKeyPress={handleKeyPress}
            placeholder="Введите сообщение..."
            rows="3"
          />
          <button
            type="submit"
            className="btn-send"
            disabled={!newMessage.trim() || !isConnected}
          >
            Отправить
          </button>
        </form>
      </div>

      {error && (
        <div className="error-message">
          {error}
          <button onClick={() => setError('')}>×</button>
        </div>
      )}
    </div>
  );
};

export default ChatWindow;