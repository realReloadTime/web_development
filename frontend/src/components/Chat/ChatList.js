import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { chatService, userService } from '../../services/api';
import './ChatList.css';

const ChatList = () => {
  const [chats, setChats] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showNewChatModal, setShowNewChatModal] = useState(false);
  const [newChatData, setNewChatData] = useState({
    type: 'private',
    user_id: '',
    group_name: '',
    participant_ids: []
  });

  const { user, isAuthenticated } = useAuth();

  useEffect(() => {
    if (isAuthenticated) {
      loadChats();
      loadUsers();
    }
  }, [isAuthenticated]);

  const loadChats = async () => {
    try {
      setLoading(true);
      const data = await chatService.getChatRooms();
      setChats(data);
    } catch (err) {
      console.error('Failed to load chats:', err);
      setError('Не удалось загрузить чаты');
    } finally {
      setLoading(false);
    }
  };

  const loadUsers = async () => {
    try {
      const data = await userService.getAllUsers();
      // Исключаем текущего пользователя из списка
      const otherUsers = data.filter(u => u.id !== user.id);
      setUsers(otherUsers);
    } catch (err) {
      console.error('Failed to load users:', err);
    }
  };

  const handleCreatePrivateChat = async () => {
    try {
      const chat = await chatService.getOrCreatePrivateChat(newChatData.user_id);
      setChats(prev => [chat, ...prev]);
      setShowNewChatModal(false);
      setNewChatData({
        type: 'private',
        user_id: '',
        group_name: '',
        participant_ids: []
      });
    } catch (err) {
      console.error('Failed to create chat:', err);
      setError('Не удалось создать чат');
    }
  };

  const handleCreateGroupChat = async () => {
    try {
      const chat = await chatService.createGroupChat(
        newChatData.group_name,
        [...newChatData.participant_ids, user.id]
      );
      setChats(prev => [chat, ...prev]);
      setShowNewChatModal(false);
      setNewChatData({
        type: 'private',
        user_id: '',
        group_name: '',
        participant_ids: []
      });
    } catch (err) {
      console.error('Failed to create group chat:', err);
      setError('Не удалось создать групповой чат');
    }
  };

  const handleSubmitNewChat = () => {
    if (newChatData.type === 'private') {
      handleCreatePrivateChat();
    } else {
      handleCreateGroupChat();
    }
  };

  const formatLastMessageTime = (timestamp) => {
    if (!timestamp) return '';

    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;

    if (diff < 24 * 60 * 60 * 1000) {
      return date.toLocaleTimeString('ru-RU', {
        hour: '2-digit',
        minute: '2-digit'
      });
    } else if (diff < 7 * 24 * 60 * 60 * 1000) {
      return date.toLocaleDateString('ru-RU', {
        weekday: 'short'
      });
    } else {
      return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit'
      });
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="auth-required">
        <h2>Требуется авторизация</h2>
        <p>Для использования чата необходимо войти в систему</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Загрузка чатов...</p>
      </div>
    );
  }

  return (
    <div className="chat-list">
      <header className="chat-list-header">
        <h1>Чаты</h1>
        <button
          className="btn-new-chat"
          onClick={() => setShowNewChatModal(true)}
        >
          Новый чат
        </button>
      </header>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="chats-container">
        {chats.length === 0 ? (
          <div className="no-chats">
            <p>У вас пока нет чатов</p>
            <button
              className="btn-start-chat"
              onClick={() => setShowNewChatModal(true)}
            >
              Начать общение
            </button>
          </div>
        ) : (
          chats.map(chat => (
            <Link
              key={chat.id}
              to={`/chat/${chat.id}`}
              className="chat-item"
            >
              <div className="chat-avatar">
                {chat.is_group ? (
                  <div className="group-avatar">
                    <span>👥</span>
                  </div>
                ) : (
                  <div className="private-avatar">
                    <span>👤</span>
                  </div>
                )}
              </div>

              <div className="chat-info">
                <div className="chat-header">
                  <h3 className="chat-title">
                    {chat.is_group
                      ? (chat.name || `Групповой чат ${chat.id}`)
                      : 'Приватный чат'}
                  </h3>
                  {chat.unread_count > 0 && (
                    <span className="unread-badge">
                      {chat.unread_count}
                    </span>
                  )}
                </div>

                <div className="chat-preview">
                  <p className="last-message">
                    {chat.last_message || 'Нет сообщений'}
                  </p>
                  <span className="last-message-time">
                    {formatLastMessageTime(chat.last_message_time)}
                  </span>
                </div>

                <div className="chat-meta">
                  <span className="participant-count">
                    {chat.participant_count} участник(ов)
                  </span>
                </div>
              </div>
            </Link>
          ))
        )}
      </div>

      {showNewChatModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2>Новый чат</h2>

            <div className="form-group">
              <label>Тип чата:</label>
              <div className="chat-type-selector">
                <button
                  className={`type-btn ${newChatData.type === 'private' ? 'active' : ''}`}
                  onClick={() => setNewChatData(prev => ({ ...prev, type: 'private' }))}
                >
                  Приватный
                </button>
                <button
                  className={`type-btn ${newChatData.type === 'group' ? 'active' : ''}`}
                  onClick={() => setNewChatData(prev => ({ ...prev, type: 'group' }))}
                >
                  Групповой
                </button>
              </div>
            </div>

            {newChatData.type === 'private' ? (
              <div className="form-group">
                <label htmlFor="user-select">Выберите пользователя:</label>
                <select
                  id="user-select"
                  value={newChatData.user_id}
                  onChange={(e) => setNewChatData(prev => ({ ...prev, user_id: e.target.value }))}
                >
                  <option value="">Выберите пользователя</option>
                  {users.map(u => (
                    <option key={u.id} value={u.id}>
                      {u.username || u.email}
                    </option>
                  ))}
                </select>
              </div>
            ) : (
              <>
                <div className="form-group">
                  <label htmlFor="group-name">Название группы:</label>
                  <input
                    type="text"
                    id="group-name"
                    value={newChatData.group_name}
                    onChange={(e) => setNewChatData(prev => ({ ...prev, group_name: e.target.value }))}
                    placeholder="Введите название группы"
                  />
                </div>

                <div className="form-group">
                  <label>Выберите участников:</label>
                  <div className="participant-selector">
                    {users.map(u => (
                      <div key={u.id} className="participant-option">
                        <input
                          type="checkbox"
                          id={`user-${u.id}`}
                          checked={newChatData.participant_ids.includes(u.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setNewChatData(prev => ({
                                ...prev,
                                participant_ids: [...prev.participant_ids, u.id]
                              }));
                            } else {
                              setNewChatData(prev => ({
                                ...prev,
                                participant_ids: prev.participant_ids.filter(id => id !== u.id)
                              }));
                            }
                          }}
                        />
                        <label htmlFor={`user-${u.id}`}>
                          {u.username || u.email}
                        </label>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}

            <div className="modal-actions">
              <button
                className="btn-primary"
                onClick={handleSubmitNewChat}
                disabled={
                  (newChatData.type === 'private' && !newChatData.user_id) ||
                  (newChatData.type === 'group' && (!newChatData.group_name || newChatData.participant_ids.length === 0))
                }
              >
                Создать чат
              </button>
              <button
                className="btn-secondary"
                onClick={() => setShowNewChatModal(false)}
              >
                Отмена
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatList;