import React, { useState, useEffect } from 'react';
import './BookForm.css';

const BookForm = ({ onSubmit, onCancel, editingBook, authors, genres }) => {
  const [formData, setFormData] = useState({
    title: '',
    author: '',
    publication_year: new Date().getFullYear(),
    genre: '',
    isbn: '',
    page_count: ''
  });

  useEffect(() => {
    if (editingBook) {
      setFormData({
        title: editingBook.title || '',
        author: editingBook.author?.toString() || '',
        publication_year: editingBook.publication_year || new Date().getFullYear(),
        genre: editingBook.genre?.toString() || '',
        isbn: editingBook.isbn || '',
        page_count: editingBook.page_count?.toString() || ''
      });
    }
  }, [editingBook]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // Преобразуем данные перед отправкой
    const submitData = {
      ...formData,
      author: parseInt(formData.author),
      genre: formData.genre ? parseInt(formData.genre) : null,
      publication_year: formData.publication_year ? parseInt(formData.publication_year) : null,
      page_count: formData.page_count ? parseInt(formData.page_count) : null
    };

    onSubmit(submitData);
  };

  return (
    <form className="book-form" onSubmit={handleSubmit}>
      <h2>{editingBook ? 'Редактировать книгу' : 'Добавить новую книгу'}</h2>

      <div className="form-group">
        <label htmlFor="title">Название:</label>
        <input
          type="text"
          id="title"
          name="title"
          value={formData.title}
          onChange={handleChange}
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="author">Автор:</label>
        <select
          id="author"
          name="author"
          value={formData.author}
          onChange={handleChange}
          required
        >
          <option value="">Выберите автора</option>
          {authors?.map(author => (
            <option key={author.id} value={author.id}>
              {`${author.second_name} ${author.first_name} ${author.third_name || ''}`}
            </option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="publication_year">Год издания:</label>
        <input
          type="number"
          id="publication_year"
          name="publication_year"
          value={formData.publication_year}
          onChange={handleChange}
          min="1000"
          max={new Date().getFullYear()}
        />
      </div>

      <div className="form-group">
        <label htmlFor="genre">Жанр:</label>
        <select
          id="genre"
          name="genre"
          value={formData.genre}
          onChange={handleChange}
        >
          <option value="">Выберите жанр</option>
          {genres?.map(genre => (
            <option key={genre.id} value={genre.id}>
              {genre.name}
            </option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="isbn">ISBN:</label>
        <input
          type="text"
          id="isbn"
          name="isbn"
          value={formData.isbn}
          onChange={handleChange}
          pattern="[0-9\-]{10,17}"
          title="Введите корректный ISBN (10 или 13 цифр, разделенных дефисами)"
        />
      </div>

      <div className="form-group">
        <label htmlFor="page_count">Количество страниц:</label>
        <input
          type="number"
          id="page_count"
          name="page_count"
          value={formData.page_count}
          onChange={handleChange}
          min="1"
        />
      </div>

      <div className="form-actions">
        <button type="submit" className="btn-primary">
          {editingBook ? 'Сохранить' : 'Добавить'}
        </button>
        <button type="button" className="btn-secondary" onClick={onCancel}>
          {editingBook ? 'Отмена' : 'Закрыть'}
        </button>
      </div>
    </form>
  );
};

export default BookForm;