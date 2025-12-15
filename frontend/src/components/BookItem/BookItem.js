import React from 'react';
import './BookItem.css';

const BookItem = ({
  book,
  authors,
  genres,
  onDelete,
  onReserve,
  currentUser,
  onEditClick,
  isBookReservedByCurrentUser
}) => {
  const getAuthorName = (authorId) => {
    const author = authors?.find(a => a.id === authorId);
    if (!author) return 'Неизвестен';

    const nameParts = [
      author.second_name,
      author.first_name,
      author.third_name
    ].filter(Boolean);

    return nameParts.join(' ');
  };

  const getGenreName = (genreId) => {
    const genre = genres?.find(g => g.id === genreId);
    return genre ? genre.name : 'Не указан';
  };

  const isBookReserved = book.reserved_by !== null && book.reserved_by !== undefined;
  const isReservedByCurrentUser = currentUser && book.reserved_by === currentUser.id;
  const canEditDelete = currentUser && (!isBookReserved || isReservedByCurrentUser);

  return (
    <div className={`book-item ${isBookReserved ? 'reserved' : ''}`}>
      <div className="book-info">
        <h3 className="book-title">{book.title}</h3>
        <div className="book-details">
          <p><strong>Автор:</strong> {getAuthorName(book.author)}</p>
          {book.publication_year && (
            <p><strong>Год издания:</strong> {book.publication_year}</p>
          )}
          {book.genre && (
            <p><strong>Жанр:</strong> {getGenreName(book.genre)}</p>
          )}
          {book.isbn && <p><strong>ISBN:</strong> {book.isbn}</p>}
          {book.page_count && <p><strong>Страниц:</strong> {book.page_count}</p>}
          {isBookReserved && (
            <p className="reserved-info">
              <strong>Статус:</strong> Забронирована
              {isReservedByCurrentUser && ' (вами)'}
            </p>
          )}
        </div>
      </div>

      <div className="book-actions">
        {currentUser ? (
          <>
            {canEditDelete && (
              <button
                className="btn-edit"
                onClick={() => onEditClick()}
              >
                Редактировать
              </button>
            )}

            {canEditDelete && (
              <button
                className="btn-delete"
                onClick={() => onDelete(book.id)}
              >
                Удалить
              </button>
            )}

            <button
              className={`btn-reserve ${isBookReserved ? 'btn-unreserve' : ''}`}
              onClick={() => onReserve(book.id, !isBookReserved)}
              disabled={isBookReserved && !isReservedByCurrentUser}
              title={isBookReserved && !isReservedByCurrentUser ?
                "Книга забронирована другим пользователем" : ""}
            >
              {isBookReserved
                ? (isReservedByCurrentUser ? 'Снять бронь' : 'Забронирована')
                : (isBookReservedByCurrentUser ? 'Вы уже забронировали' : 'Забронировать')}
            </button>
          </>
        ) : (
          <div className="login-prompt">
            <p>Войдите для управления</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default BookItem;