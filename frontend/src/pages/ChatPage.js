import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import ChatList from '../components/Chat/ChatList';
import ChatWindow from '../components/Chat/ChatWindow';

const ChatPage = () => {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  return (
    <div className="chat-page">
      <Routes>
        <Route path="/" element={<ChatList />} />
        <Route path="/:roomId" element={<ChatWindow />} />
      </Routes>
    </div>
  );
};

export default ChatPage;