import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { chatService } from '../../services/api';
import './Navbar.css';

const Navbar = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [unreadCount, setUnreadCount] = useState(0);
  const [showChats, setShowChats] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      loadUnreadCount();

      // Обновляем счетчик каждые 30 секунд
      const interval = setInterval(loadUnreadCount, 30000);
      return () => clearInterval(interval);
    }
  }, [isAuthenticated]);

  const loadUnreadCount = async () => {
    try {
      const data = await chatService.getUnreadCount();
      setUnreadCount(data.unread_count);
    } catch (err) {
      console.error('Failed to load unread count:', err);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path) => {
    if (path === '/chat') {
      return location.pathname.startsWith('/chat') ? 'active' : '';
    }
    return location.pathname === path ? 'active' : '';
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          Библиотека "Солнышко"
        </Link>

        <div className="navbar-links">
          {isAuthenticated ? (
            <>
              <Link to="/" className={`nav-link ${isActive('/')}`}>
                Книги
              </Link>
              <Link to="/bookings" className={`nav-link ${isActive('/bookings')}`}>
                Бронирования
              </Link>

              <div
                className={`nav-link chat-link ${isActive('/chat')}`}
                onMouseEnter={() => setShowChats(true)}
                onMouseLeave={() => setShowChats(false)}
              >
                <Link to="/chat" className="chat-link-main">
                  Чаты
                  {unreadCount > 0 && (
                    <span className="unread-chat-count">
                      {unreadCount > 9 ? '9+' : unreadCount}
                    </span>
                  )}
                </Link>

                {showChats && (
                  <div className="chat-dropdown">
                    <Link to="/chat" className="chat-dropdown-item">
                      Все чаты
                      {unreadCount > 0 && (
                        <span className="unread-badge">{unreadCount}</span>
                      )}
                    </Link>
                    <Link to="/chat/new" className="chat-dropdown-item">
                      Новый чат
                    </Link>
                  </div>
                )}
              </div>

              <span className="navbar-user">
                {user?.username || user?.email}
              </span>
              <button onClick={handleLogout} className="btn-logout">
                Выйти
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className={`nav-link ${isActive('/login')}`}>
                Войти
              </Link>
              <Link to="/register" className={`nav-link ${isActive('/register')}`}>
                Регистрация
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;