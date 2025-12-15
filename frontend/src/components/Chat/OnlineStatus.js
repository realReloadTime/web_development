import React, { useState, useEffect } from 'react';
import { chatService } from '../../services/api';

const OnlineStatus = ({ roomId, userId }) => {
  const [isOnline, setIsOnline] = useState(false);

  useEffect(() => {
    if (!roomId || !userId) return;

    const checkOnlineStatus = async () => {
      try {
        const data = await chatService.getOnlineUsers(roomId);
        const userOnline = data.online_users?.some(u => u.user_id === userId);
        setIsOnline(userOnline);
      } catch (err) {
        console.error('Failed to check online status:', err);
      }
    };

    checkOnlineStatus();

    // Проверяем статус каждые 10 секунд
    const interval = setInterval(checkOnlineStatus, 10000);
    return () => clearInterval(interval);
  }, [roomId, userId]);

  return (
    <span className={`online-status ${isOnline ? 'online' : 'offline'}`}>
      {isOnline ? '🟢' : '🔴'}
    </span>
  );
};

export default OnlineStatus;