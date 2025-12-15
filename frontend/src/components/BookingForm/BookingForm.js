import React, { useState, useEffect } from 'react';
import './BookingForm.css';

const BookingForm = ({ onSubmit, onCancel, editingBooking, books, users, currentUserId }) => {
  const [formData, setFormData] = useState({
    user_id: currentUserId || '',
    book_id: '',
    take_date: '',
    end_date: ''
  });

  useEffect(() => {
    if (editingBooking) {
      setFormData({
        user_id: editingBooking.user_id?.toString() || '',
        book_id: editingBooking.book_id?.toString() || '',
        take_date: editingBooking.take_date ? editingBooking.take_date.split('T')[0] : '',
        end_date: editingBooking.end_date ? editingBooking.end_date.split('T')[0] : ''
      });
    } else {
      // Устанавливаем текущую дату для нового бронирования
      const today = new Date().toISOString().split('T')[0];
      const nextWeek = new Date();
      nextWeek.setDate(nextWeek.getDate() + 7);
      const nextWeekStr = nextWeek.toISOString().split('T')[0];

      setFormData({
        user_id: currentUserId || '',
        book_id: '',
        take_date: today,
        end_date: nextWeekStr
      });
    }
  }, [editingBooking, currentUserId]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // Преобразуем даты в ISO формат
    const submitData = {
      ...formData,
      user_id: parseInt(formData.user_id),
      book_id: parseInt(formData.book_id),
      take_date: formData.take_date ? `${formData.take_date}T00:00:00` : null,
      end_date: formData.end_date ? `${formData.end_date}T00:00:00` : null
    };

    onSubmit(submitData);
  };

  // Фильтруем книги: показываем только те, которые не забронированы
  const availableBooks = books.filter(book => !book.reserved_by);

  return (
    <form className="booking-form" onSubmit={handleSubmit}>
      <h2>{editingBooking ? 'Редактировать бронирование' : 'Новое бронирование'}</h2>

      <div className="form-group">
        <label htmlFor="user_id">Пользователь:</label>
        <select
          id="user_id"
          name="user_id"
          value={formData.user_id}
          onChange={handleChange}
          required
          disabled={!users.length} // Если нет доступа к списку пользователей
        >
          <option value="">Выберите пользователя</option>
          {users.length > 0 ? (
            users.map(user => (
              <option key={user.id} value={user.id}>
                {user.username || user.email}
              </option>
            ))
          ) : (
            <option value={currentUserId}>Вы (текущий пользователь)</option>
          )}
        </select>
        {!users.length && (
          <p className="form-hint">Бронирование будет создано для вас</p>
        )}
      </div>

      <div className="form-group">
        <label htmlFor="book_id">Книга:</label>
        <select
          id="book_id"
          name="book_id"
          value={formData.book_id}
          onChange={handleChange}
          required
        >
          <option value="">Выберите книгу</option>
          {availableBooks.map(book => (
            <option key={book.id} value={book.id}>
              {book.title} ({book.author_name || `Автор #${book.author}`})
            </option>
          ))}
        </select>
        {availableBooks.length === 0 && (
          <p className="form-error">Нет доступных книг для бронирования</p>
        )}
      </div>

      <div className="form-group">
        <label htmlFor="take_date">Дата взятия:</label>
        <input
          type="date"
          id="take_date"
          name="take_date"
          value={formData.take_date}
          onChange={handleChange}
          required
          min={new Date().toISOString().split('T')[0]}
        />
      </div>

      <div className="form-group">
        <label htmlFor="end_date">Дата возврата:</label>
        <input
          type="date"
          id="end_date"
          name="end_date"
          value={formData.end_date}
          onChange={handleChange}
          min={formData.take_date || new Date().toISOString().split('T')[0]}
        />
        <p className="form-hint">Оставьте пустым для бессрочного бронирования</p>
      </div>

      <div className="form-actions">
        <button
          type="submit"
          className="btn-primary"
          disabled={availableBooks.length === 0}
        >
          {editingBooking ? 'Сохранить' : 'Создать'}
        </button>
        <button type="button" className="btn-secondary" onClick={onCancel}>
          Отмена
        </button>
      </div>
    </form>
  );
};

export default BookingForm;