export const mockBooks = [
  {
    id: 1,
    title: "Мастер и Маргарита",
    author: 1,
    publication_year: 1967,
    genre: 1,
    isbn: "978-5-699-12345-6",
    page_count: 480,
    reserved_by: null
  },
  {
    id: 2,
    title: "Преступление и наказание",
    author: 2,
    publication_year: 1866,
    genre: 2,
    isbn: "978-5-699-12346-3",
    page_count: 608,
    reserved_by: null
  },
  {
    id: 3,
    title: "Война и мир",
    author: 3,
    publication_year: 1869,
    genre: 3,
    isbn: "978-5-699-12347-0",
    page_count: 1225,
    reserved_by: 1
  }
];

export const mockAuthors = [
  {
    id: 1,
    first_name: "Михаил",
    second_name: "Булгаков",
    third_name: "Афанасьевич",
    birth_date: "1891-05-15"
  },
  {
    id: 2,
    first_name: "Фёдор",
    second_name: "Достоевский",
    third_name: "Михайлович",
    birth_date: "1821-11-11"
  },
  {
    id: 3,
    first_name: "Лев",
    second_name: "Толстой",
    third_name: "Николаевич",
    birth_date: "1828-09-09"
  }
];

export const mockGenres = [
  { id: 1, name: "Фантастика" },
  { id: 2, name: "Детектив" },
  { id: 3, name: "Роман" },
  { id: 4, name: "Классика" }
];

export const mockUsers = [
  {
    id: 1,
    username: "ivanov",
    email: "ivanov@example.com",
    password_hash: "hashed_password_1"
  },
  {
    id: 2,
    username: "petrov",
    email: "petrov@example.com",
    password_hash: "hashed_password_2"
  }
];