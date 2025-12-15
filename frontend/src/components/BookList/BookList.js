import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { bookService, authorService, genreService, bookingService } from '../../services/api';
import BookItem from '../BookItem/BookItem';
import BookForm from '../BookForm/BookForm';
import './BookList.css';

const BookList = () => {
  const [books, setBooks] = useState([]);
  const [authors, setAuthors] = useState([]);
  const [genres, setGenres] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingBook, setEditingBook] = useState(null);

  const { user, isAuthenticated } = useAuth();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError('');

      const [booksData, authorsData, genresData, bookingsData] = await Promise.all([
        bookService.getBooks(),
        authorService.getAuthors(),
        genreService.getGenres(),
        bookingService.getBookings()
      ]);

      setBooks(booksData);
      setAuthors(authorsData);
      setGenres(genresData);
      setBookings(bookingsData);
    } catch (err) {
      console.error('Failed to load data:', err);
      setError('Не удалось загрузить данные. Пожалуйста, попробуйте позже.');
    } finally {
      setLoading(false);
    }
  };

  // Проверка, забронирована ли книга текущим пользователем
  const isBookReservedByCurrentUser = (bookId) => {
    const activeBooking = bookings.find(b =>
      b.book_id === bookId &&
      b.user_id === user?.id &&
      (!b.end_date || new Date(b.end_date) > new Date())
    );
    return !!activeBooking;
  };

  // Найти активное бронирование для книги
  const getActiveBookingForBook = (bookId) => {
    return bookings.find(b =>
      b.book_id === bookId &&
      (!b.end_date || new Date(b.end_date) > new Date())
    );
  };

  const handleAddBook = async (formData) => {
    try {
      const bookData = {
        title: formData.title,
        author: parseInt(formData.author),
        genre: formData.genre ? parseInt(formData.genre) : null,
        publication_year: formData.publication_year ? parseInt(formData.publication_year) : null,
        isbn: formData.isbn || null,
        page_count: formData.page_count ? parseInt(formData.page_count) : null
      };

      const newBook = await bookService.createBook(bookData);
      setBooks(prev => [...prev, newBook]);
      setShowForm(false);
      setError('');
    } catch (err) {
      console.error('Failed to add book:', err);
      setError('Не удалось добавить книгу. Проверьте введенные данные.');
    }
  };

  const handleEditBook = async (bookId, formData) => {
    try {
      const bookData = {
        title: formData.title,
        author: parseInt(formData.author),
        genre: formData.genre ? parseInt(formData.genre) : null,
        publication_year: formData.publication_year ? parseInt(formData.publication_year) : null,
        isbn: formData.isbn || null,
        page_count: formData.page_count ? parseInt(formData.page_count) : null
      };

      const updatedBook = await bookService.updateBook(bookId, bookData);
      setBooks(prev => prev.map(book =>
        book.id === bookId ? updatedBook : book
      ));
      setEditingBook(null);
      setShowForm(false);
      setError('');
    } catch (err) {
      console.error('Failed to update book:', err);
      setError('Не удалось обновить книгу. Проверьте введенные данные.');
    }
  };

  const handleDeleteBook = async (bookId) => {
    if (!window.confirm('Вы уверены, что хотите удалить эту книгу?')) {
      return;
    }

    try {
      // Проверяем, есть ли активные бронирования для этой книги
      const activeBooking = getActiveBookingForBook(bookId);
      if (activeBooking) {
        alert('Нельзя удалить книгу, которая забронирована. Сначала завершите бронирование.');
        return;
      }

      await bookService.deleteBook(bookId);
      setBooks(prev => prev.filter(book => book.id !== bookId));
      setError('');
    } catch (err) {
      console.error('Failed to delete book:', err);
      setError('Не удалось удалить книгу.');
    }
  };

  const handleReserveBook = async (bookId, reserve) => {
    try {
      const book = books.find(b => b.id === bookId);
      if (!book) return;

      if (reserve) {
        // Проверяем, не забронирована ли уже книга
        if (book.reserved_by) {
          setError('Книга уже забронирована другим пользователем');
          return;
        }

        // Проверяем, не забронировал ли уже текущий пользователь эту книгу
        if (isBookReservedByCurrentUser(bookId)) {
          setError('Вы уже забронировали эту книгу');
          return;
        }

        // Создаем бронирование
        await bookingService.createBooking({
          user_id: user.id,
          book_id: bookId,
          take_date: new Date().toISOString()
        });

        // Обновляем книгу - отмечаем как забронированную
        const updatedBook = {
          ...book,
          reserved_by: user.id
        };

        await bookService.updateBook(bookId, updatedBook);

      } else {
        // Снимаем бронь
        // Находим активное бронирование для этой книги текущим пользователем
        const userBooking = bookings.find(b =>
          b.book_id === bookId &&
          b.user_id === user.id &&
          (!b.end_date || new Date(b.end_date) > new Date())
        );

        if (userBooking) {
          // Завершаем бронирование
          await bookingService.completeBooking(userBooking.id);
        }

        // Обновляем книгу - снимаем бронь
        const updatedBook = {
          ...book,
          reserved_by: null
        };

        await bookService.updateBook(bookId, updatedBook);
      }

      // Обновляем данные
      loadData();
    } catch (err) {
      console.error('Failed to update booking:', err);
      setError('Не удалось обновить статус бронирования.');
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Загрузка данных...</p>
      </div>
    );
  }

  return (
    <div className="book-list">
      <header className="book-list-header">
        <h1>Библиотека книг</h1>
        <div className="header-actions">
          <button
            className="btn-refresh"
            onClick={loadData}
            title="Обновить данные"
          >
            ⟳
          </button>
          {isAuthenticated && (
            <button
              className="btn-add"
              onClick={() => {
                setEditingBook(null);
                setShowForm(true);
              }}
            >
              Добавить книгу
            </button>
          )}
        </div>
      </header>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {!isAuthenticated && (
        <div className="auth-warning">
          <p>Для управления книгами необходимо войти в систему</p>
        </div>
      )}

      {showForm && (
        <div className="form-modal">
          <div className="form-modal-content">
            <BookForm
              onSubmit={editingBook ?
                (data) => handleEditBook(editingBook.id, data) :
                handleAddBook}
              onCancel={() => {
                setShowForm(false);
                setEditingBook(null);
              }}
              editingBook={editingBook}
              authors={authors}
              genres={genres}
            />
          </div>
        </div>
      )}

      <div className="books-container">
        {books.length === 0 ? (
          <div className="no-books">
            <p>Книги не найдены</p>
            {isAuthenticated && (
              <button
                className="btn-add-first"
                onClick={() => setShowForm(true)}
              >
                Добавить первую книгу
              </button>
            )}
          </div>
        ) : (
          books.map(book => (
            <BookItem
              key={book.id}
              book={book}
              authors={authors}
              genres={genres}
              onEdit={(bookId, data) => handleEditBook(bookId, data)}
              onDelete={handleDeleteBook}
              onReserve={handleReserveBook}
              currentUser={user}
              onEditClick={() => {
                setEditingBook(book);
                setShowForm(true);
              }}
              isBookReservedByCurrentUser={isBookReservedByCurrentUser(book.id)}
            />
          ))
        )}
      </div>
    </div>
  );
};

export default BookList;