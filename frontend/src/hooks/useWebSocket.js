import { useState, useEffect, useCallback, useRef } from 'react';

export const useWebSocket = (roomId, userId, onMessage, onError) => {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState([]);
  const [typingUsers, setTypingUsers] = useState({});
  const [onlineUsers, setOnlineUsers] = useState([]);

  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  // Используем ref для хранения callback функций, чтобы они не менялись при каждом рендере
  const onMessageRef = useRef(onMessage);
  const onErrorRef = useRef(onError);

  // Обновляем ref при изменении callback функций
  useEffect(() => {
    onMessageRef.current = onMessage;
    onErrorRef.current = onError;
  }, [onMessage, onError]);

  const connect = useCallback(() => {
    if (!roomId || !userId) return;

    // Закрываем существующее соединение
    if (wsRef.current) {
      wsRef.current.close();
    }

    const wsUrl = `ws://localhost:8000/chat/ws/${roomId}?user_id=${userId}`;
    wsRef.current = new WebSocket(wsUrl);

    wsRef.current.onopen = () => {
      setIsConnected(true);
      if (onErrorRef.current) onErrorRef.current(null);
    };

    wsRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        switch (data.type) {
          case 'message':
            setMessages(prev => [...prev, data.message]);
            break;

          case 'history':
            setMessages(data.messages || []);
            break;

          case 'typing':
            setTypingUsers(prev => ({
              ...prev,
              [data.user_id]: data.is_typing ? Date.now() : null
            }));
            break;

          case 'online_users':
            setOnlineUsers(data.users || []);
            break;

          case 'system':
            console.log('System message:', data.message);
            break;

          case 'error':
            if (onErrorRef.current) onErrorRef.current(data.error);
            break;

          default:
            if (onMessageRef.current) onMessageRef.current(data);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    wsRef.current.onclose = (event) => {
      setIsConnected(false);

      // Пытаемся переподключиться через 3 секунды
      if (event.code !== 1000) { // Не нормальное закрытие
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, 3000);
      }
    };

    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      if (onErrorRef.current) onErrorRef.current('Ошибка соединения с чатом');
    };
  }, [roomId, userId]); // Убрали onMessage и onError из зависимостей

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    if (wsRef.current) {
      wsRef.current.close(1000, 'Пользователь покинул чат');
      wsRef.current = null;
    }

    setIsConnected(false);
    setMessages([]);
    setTypingUsers({});
    setOnlineUsers([]);
  }, []);

  const sendMessage = useCallback((content) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'message',
        content
      }));
      return true;
    }
    return false;
  }, []);

  const sendTypingIndicator = useCallback((isTyping) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'typing',
        is_typing: isTyping
      }));
      return true;
    }
    return false;
  }, []);

  const markAsRead = useCallback((messageId) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'read',
        message_id: messageId
      }));
      return true;
    }
    return false;
  }, []);

  useEffect(() => {
    if (roomId && userId) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [roomId, userId, connect, disconnect]);

  return {
    isConnected,
    messages,
    typingUsers,
    onlineUsers,
    sendMessage,
    sendTypingIndicator,
    markAsRead,
    disconnect,
    reconnect: connect
  };
};