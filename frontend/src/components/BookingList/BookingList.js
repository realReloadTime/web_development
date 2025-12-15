import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { bookingService, bookService, userService } from '../../services/api';
import BookingForm from '../BookingForm/BookingForm';
import './BookingList.css';

const BookingList = () => {
  const [bookings, setBookings] = useState([]);
  const [books, setBooks] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingBooking, setEditingBooking] = useState(null);

  const { user, isAuthenticated } = useAuth();

  useEffect(() => {
    if (isAuthenticated) {
      loadData();
    }
  }, [isAuthenticated]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError('');

      // Загружаем бронирования
      const bookingsData = await bookingService.getBookings();

      // Загружаем книги для отображения названий
      const booksData = await bookService.getBooks();

      // Если пользователь админ, загружаем всех пользователей
      let usersData = [];
      try {
        usersData = await userService.getAllUsers();
      } catch (err) {
        console.log('Не удалось загрузить пользователей');
      }

      setBookings(bookingsData);
      setBooks(booksData);
      setUsers(usersData);
    } catch (err) {
      console.error('Failed to load data:', err);
      setError('Не удалось загрузить данные бронирований');
    } finally {
      setLoading(false);
    }
  };

  const getBookTitle = (bookId) => {
    const book = books.find(b => b.id === bookId);
    return book ? book.title : `Книга #${bookId}`;
  };

  const getUserName = (userId) => {
    if (userId === user?.id) return 'Вы';

    const userData = users.find(u => u.id === userId);
    return userData ? userData.username || userData.email : `Пользователь #${userId}`;
  };

  const handleAddBooking = async (formData) => {
    try {
      const bookingData = {
        user_id: parseInt(formData.user_id),
        book_id: parseInt(formData.book_id),
        take_date: formData.take_date || null,
        end_date: formData.end_date || null
      };

      const newBooking = await bookingService.createBooking(bookingData);

      // Обновляем книгу - отмечаем как забронированную
      const book = books.find(b => b.id === bookingData.book_id);
      if (book) {
        await bookService.updateBook(bookingData.book_id, {
          ...book,
          reserved_by: bookingData.user_id
        });
      }

      setBookings(prev => [...prev, newBooking]);
      setShowForm(false);
      setError('');

      // Перезагружаем данные для обновления состояния
      loadData();
    } catch (err) {
      console.error('Failed to add booking:', err);
      setError('Не удалось добавить бронирование');
    }
  };

  const handleEditBooking = async (bookingId, formData) => {
    try {
      const bookingData = {
        user_id: parseInt(formData.user_id),
        book_id: parseInt(formData.book_id),
        take_date: formData.take_date || null,
        end_date: formData.end_date || null
      };

      // Получаем текущее бронирование для проверки
      const currentBooking = bookings.find(b => b.id === bookingId);

      const updatedBooking = await bookingService.updateBooking(bookingId, bookingData);

      // Если изменилась книга или пользователь, обновляем статус книг
      if (currentBooking && currentBooking.book_id !== bookingData.book_id) {
        // Освобождаем старую книгу
        const oldBook = books.find(b => b.id === currentBooking.book_id);
        if (oldBook) {
          await bookService.updateBook(currentBooking.book_id, {
            ...oldBook,
            reserved_by: null
          });
        }

        // Бронируем новую книгу
        const newBook = books.find(b => b.id === bookingData.book_id);
        if (newBook) {
          await bookService.updateBook(bookingData.book_id, {
            ...newBook,
            reserved_by: bookingData.user_id
          });
        }
      }

      setBookings(prev => prev.map(booking =>
        booking.id === bookingId ? updatedBooking : booking
      ));
      setEditingBooking(null);
      setShowForm(false);
      setError('');

      // Перезагружаем данные
      loadData();
    } catch (err) {
      console.error('Failed to update booking:', err);
      setError('Не удалось обновить бронирование');
    }
  };

  const handleDeleteBooking = async (bookingId) => {
    if (!window.confirm('Вы уверены, что хотите удалить это бронирование?')) {
      return;
    }

    try {
      const bookingToDelete = bookings.find(b => b.id === bookingId);

      await bookingService.deleteBooking(bookingId);

      // Освобождаем книгу при удалении активного бронирования
      if (bookingToDelete && !bookingToDelete.end_date) {
        const book = books.find(b => b.id === bookingToDelete.book_id);
        if (book) {
          await bookService.updateBook(bookingToDelete.book_id, {
            ...book,
            reserved_by: null
          });
        }
      }

      setBookings(prev => prev.filter(booking => booking.id !== bookingId));
      setError('');

      // Перезагружаем данные
      loadData();
    } catch (err) {
      console.error('Failed to delete booking:', err);
      setError('Не удалось удалить бронирование');
    }
  };

  const handleCompleteBooking = async (bookingId) => {
    try {
      const bookingToComplete = bookings.find(b => b.id === bookingId);

      const completedBooking = await bookingService.completeBooking(bookingId);

      // Освобождаем книгу при завершении бронирования
      if (bookingToComplete) {
        const book = books.find(b => b.id === bookingToComplete.book_id);
        if (book) {
          await bookService.updateBook(bookingToComplete.book_id, {
            ...book,
            reserved_by: null
          });
        }
      }

      setBookings(prev => prev.map(booking =>
        booking.id === bookingId ? completedBooking : booking
      ));
      setError('');

      // Перезагружаем данные
      loadData();
    } catch (err) {
      console.error('Failed to complete booking:', err);
      setError('Не удалось завершить бронирование');
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Не указана';
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  const isActiveBooking = (booking) => {
    if (!booking.end_date) return true;
    const endDate = new Date(booking.end_date);
    return endDate > new Date();
  };

  if (!isAuthenticated) {
    return (
      <div className="auth-required">
        <h2>Требуется авторизация</h2>
        <p>Для просмотра бронирований необходимо войти в систему</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Загрузка бронирований...</p>
      </div>
    );
  }

  return (
    <div className="booking-list">
      <header className="booking-list-header">
        <h1>Управление бронированиями</h1>
        <button
          className="btn-add"
          onClick={() => {
            setEditingBooking(null);
            setShowForm(true);
          }}
        >
          Новое бронирование
        </button>
      </header>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {showForm && (
        <div className="form-modal">
          <div className="form-modal-content">
            <BookingForm
              onSubmit={editingBooking ?
                (data) => handleEditBooking(editingBooking.id, data) :
                handleAddBooking}
              onCancel={() => {
                setShowForm(false);
                setEditingBooking(null);
              }}
              editingBooking={editingBooking}
              books={books}
              users={users}
              currentUserId={user?.id}
            />
          </div>
        </div>
      )}

      {bookings.length === 0 ? (
        <div className="no-bookings">
          <p>Бронирования не найдены</p>
          <button
            className="btn-add-first"
            onClick={() => setShowForm(true)}
          >
            Создать первое бронирование
          </button>
        </div>
      ) : (
        <div className="bookings-container">
          <table className="bookings-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Книга</th>
                <th>Пользователь</th>
                <th>Дата взятия</th>
                <th>Дата возврата</th>
                <th>Статус</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              {bookings.map(booking => {
                const active = isActiveBooking(booking);
                return (
                  <tr key={booking.id} className={active ? 'active-booking' : 'completed-booking'}>
                    <td>{booking.id}</td>
                    <td>{getBookTitle(booking.book_id)}</td>
                    <td>{getUserName(booking.user_id)}</td>
                    <td>{formatDate(booking.take_date)}</td>
                    <td>{formatDate(booking.end_date)}</td>
                    <td>
                      <span className={`booking-status ${active ? 'status-active' : 'status-completed'}`}>
                        {active ? 'Активно' : 'Завершено'}
                      </span>
                    </td>
                    <td>
                      <div className="booking-actions">
                        <button
                          className="btn-edit"
                          onClick={() => {
                            setEditingBooking(booking);
                            setShowForm(true);
                          }}
                        >
                          Изменить
                        </button>

                        {active && (
                          <button
                            className="btn-complete"
                            onClick={() => handleCompleteBooking(booking.id)}
                          >
                            Завершить
                          </button>
                        )}

                        <button
                          className="btn-delete"
                          onClick={() => handleDeleteBooking(booking.id)}
                        >
                          Удалить
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default BookingList;