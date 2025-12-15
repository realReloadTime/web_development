const API_URL = 'http://localhost:8000';

// Общая функция для выполнения fetch запросов
const fetchApi = async (endpoint, options = {}) => {
  const token = localStorage.getItem('access_token');
  const defaultHeaders = {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  };


  const response = await fetch(`${API_URL}${endpoint}`, {
    headers: defaultHeaders,
    ...options
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Попробуем обновить токен
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const refreshResponse = await fetch(`${API_URL}/users/refresh`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${refreshToken}`
            }
          });

          if (refreshResponse.ok) {
            const data = await refreshResponse.json();
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('refresh_token', data.refresh_token);

            // Повторим исходный запрос с новым токеном
            return fetchApi(endpoint, options);
          }
        } catch (error) {
          console.error('Failed to refresh token:', error);
        }
      }

      // Если не удалось обновить токен, делаем logout
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }

    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  return response;
};

// Сервисы для работы с API
export const bookService = {
  getBooks: () => fetchApi('/books').then(res => res.json()),
  getBook: (id) => fetchApi(`/books/${id}`).then(res => res.json()),
  createBook: (data) => fetchApi('/books', {
    method: 'POST',
    body: JSON.stringify(data)
  }).then(res => res.json()),
  updateBook: (id, data) => fetchApi(`/books/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  }).then(res => res.json()),
  deleteBook: (id) => fetchApi(`/books/${id}`, {
    method: 'DELETE'
  }),
};

export const authorService = {
  getAuthors: () => fetchApi('/authors').then(res => res.json()),
  getAuthor: (id) => fetchApi(`/authors/${id}`).then(res => res.json()),
  createAuthor: (data) => fetchApi('/authors', {
    method: 'POST',
    body: JSON.stringify(data)
  }).then(res => res.json()),
  updateAuthor: (id, data) => fetchApi(`/authors/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  }).then(res => res.json()),
  deleteAuthor: (id) => fetchApi(`/authors/${id}`, {
    method: 'DELETE'
  }),
};

export const genreService = {
  getGenres: () => fetchApi('/genres').then(res => res.json()),
  getGenre: (id) => fetchApi(`/genres/${id}`).then(res => res.json()),
  createGenre: (data) => fetchApi('/genres', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: new URLSearchParams(data)
  }).then(res => res.json()),
  updateGenre: (id, data) => fetchApi(`/genres/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  }).then(res => res.json()),
  deleteGenre: (id) => fetchApi(`/genres/${id}`, {
    method: 'DELETE'
  }),
};

export const bookingService = {
  getBookings: () => fetchApi('/bookings').then(res => res.json()),
  getBooking: (id) => fetchApi(`/bookings/${id}`).then(res => res.json()),
  createBooking: (data) => fetchApi('/bookings', {
    method: 'POST',
    body: JSON.stringify(data)
  }).then(res => res.json()),
  updateBooking: (id, data) => fetchApi(`/bookings/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  }).then(res => res.json()),
  deleteBooking: (id) => fetchApi(`/bookings/${id}`, {
    method: 'DELETE'
  }),
  completeBooking: (id) => fetchApi(`/bookings/${id}/complete`, {
    method: 'POST'
  }).then(res => res.json()),
};

export const userService = {
  getAllUsers: () => fetchApi('/users/all').then(res => res.json()),
  getCurrentUser: () => fetchApi('/users/me').then(res => res.json()),
  updateUser: (data) => fetchApi('/users/me', {
    method: 'PATCH',
    body: JSON.stringify(data)
  }).then(res => res.json()),
  deleteUser: () => fetchApi('/users/me', {
    method: 'DELETE'
  }),
};