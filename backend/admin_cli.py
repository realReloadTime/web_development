import asyncio
import getpass

from backend.service.user import get_user_service, UserService
from backend.service.author import get_author_service, AuthorService
from backend.service.book import get_book_service, BookService
from backend.service.genre import get_genre_service, GenreService
from backend.service.booking import get_booking_service, BookingService
from backend.schemas.user import UserRegister
from backend.schemas.author import AuthorFull
from backend.schemas.book import BookFull
from backend.schemas.genre import GenreDefault
from backend.schemas.booking import BookingDefault
from backend.security.authorization import verify_password


class AdminCLI:
    def __init__(self):
        self.user_service: UserService | None = None
        self.author_service: AuthorService | None = None
        self.book_service: BookService | None = None
        self.genre_service: GenreService | None = None
        self.booking_service: BookingService | None = None
        self.current_user = None

    async def initialize_services(self):
        """Инициализация всех сервисов"""
        self.user_service = await get_user_service()
        self.author_service = await get_author_service()
        self.book_service = await get_book_service()
        self.genre_service = await get_genre_service()
        self.booking_service = await get_booking_service()

    async def authenticate(self) -> bool:
        """Аутентификация администратора"""
        print("\n" + "=" * 50)
        print("АДМИНИСТРАТИВНАЯ КОНСОЛЬ")
        print("=" * 50)

        email = input("Введите email: ").strip()
        password = getpass.getpass("Введите пароль: ")

        try:
            user_repo = (await get_user_service()).user_repository
            user = await user_repo.get_user_by_email(email)

            if user and verify_password(password, str(user.password_hash)):
                self.current_user = user
                print(f"\n✅ Успешный вход! Добро пожаловать, {user.email}")
                return True
            else:
                print("\n❌ Неверные учетные данные!")
                return False
        except Exception as e:
            print(f"\n❌ Ошибка при аутентификации: {e}")
            return False

    async def show_main_menu(self):
        """Главное меню администратора"""
        while True:
            print("\n" + "=" * 50)
            print("ГЛАВНОЕ МЕНЮ")
            print("=" * 50)
            print("1. Управление пользователями")
            print("2. Управление авторами")
            print("3. Управление книгами")
            print("4. Управление жанрами")
            print("5. Управление бронированиями")
            print("6. Поиск записей")
            print("7. Выход")

            choice = input("\nВыберите действие (1-7): ").strip()

            if choice == "1":
                await self.manage_users()
            elif choice == "2":
                await self.manage_authors()
            elif choice == "3":
                await self.manage_books()
            elif choice == "4":
                await self.manage_genres()
            elif choice == "5":
                await self.manage_bookings()
            elif choice == "6":
                await self.search_records()
            elif choice == "7":
                print("\nДо свидания!")
                break
            else:
                print("\n❌ Неверный выбор!")

    async def manage_users(self):
        """Управление пользователями"""
        while True:
            print("\n" + "-" * 40)
            print("УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ")
            print("-" * 40)
            print("1. Показать всех пользователей")
            print("2. Добавить пользователя")
            print("3. Найти пользователя по ID")
            print("4. Найти пользователя по email")
            print("5. Обновить пользователя")
            print("6. Удалить пользователя")
            print("7. Назад")

            choice = input("\nВыберите действие (1-7): ").strip()

            if choice == "1":
                await self.show_all_users()
            elif choice == "2":
                await self.create_user()
            elif choice == "3":
                await self.get_user_by_id()
            elif choice == "4":
                await self.get_user_by_email()
            elif choice == "5":
                await self.update_user()
            elif choice == "6":
                await self.delete_user()
            elif choice == "7":
                break
            else:
                print("\n❌ Неверный выбор!")

    async def show_all_users(self):
        """Показать всех пользователей"""
        try:
            users = await self.user_service.get_all()
            if not users:
                print("\n📭 Нет зарегистрированных пользователей")
                return

            print("\n" + "=" * 60)
            print("СПИСОК ПОЛЬЗОВАТЕЛЕЙ")
            print("=" * 60)
            for user in users:
                print(f"ID: {user.id}")
                print(f"Email: {user.email}")
                print(f"Username: {user.username or 'Не установлен'}")
                print("-" * 40)
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

    async def create_user(self):
        """Создать нового пользователя"""
        try:
            print("\nСОЗДАНИЕ НОВОГО ПОЛЬЗОВАТЕЛЯ")
            print("-" * 30)

            email = input("Email: ").strip()
            password = getpass.getpass("Пароль: ")
            password_confirm = getpass.getpass("Подтвердите пароль: ")

            user_data = UserRegister(
                email=email,
                password=password,
                password_confirm=password_confirm
            )

            user = await self.user_service.create_user(user_data)
            print(f"\n✅ Пользователь создан! ID: {user.id}")

        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

    async def get_user_by_id(self):
        """Найти пользователя по ID"""
        try:
            user_id = input("\nВведите ID пользователя: ").strip()
            if not user_id.isdigit():
                print("❌ ID должен быть числом!")
                return

            user_repo = (await get_user_service()).user_repository
            user = await user_repo.get_user_by_id(int(user_id))

            if user:
                print(f"\n✅ Найден пользователь:")
                print(f"ID: {user.id}")
                print(f"Email: {user.email}")
                print(f"Username: {user.username or 'Не установлен'}")
            else:
                print(f"\n❌ Пользователь с ID {user_id} не найден")

        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

    async def get_user_by_email(self):
        """Найти пользователя по email"""
        try:
            email = input("\nВведите email пользователя: ").strip()
            user_repo = (await get_user_service()).user_repository
            user = await user_repo.get_user_by_email(email)

            if user:
                print(f"\n✅ Найден пользователь:")
                print(f"ID: {user.id}")
                print(f"Email: {user.email}")
                print(f"Username: {user.username or 'Не установлен'}")
            else:
                print(f"\n❌ Пользователь с email {email} не найден")

        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

    async def update_user(self):
        """Обновить данные пользователя"""
        try:
            user_id = input("\nВведите ID пользователя для обновления: ").strip()
            if not user_id.isdigit():
                print("❌ ID должен быть числом!")
                return

            user_repo = (await get_user_service()).user_repository
            user = await user_repo.get_user_by_id(int(user_id))

            if not user:
                print(f"\n❌ Пользователь с ID {user_id} не найден")
                return

            print(f"\nТекущие данные пользователя {user.email}:")
            print(f"Username: {user.username or 'Не установлен'}")

            print("\nВведите новые данные (оставьте пустым, чтобы не менять):")
            username = input("Новое имя пользователя: ").strip() or None
            email = input("Новый email: ").strip() or None

            update_data = {}
            if username is not None:
                update_data['username'] = username
            if email is not None:
                update_data['email'] = email

            if update_data:
                updated_user = await user_repo.update_user(int(user_id), **update_data)
                print(f"\n✅ Данные пользователя обновлены!")
            else:
                print("\n⚠️  Ничего не изменено")

        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

    async def delete_user(self):
        """Удалить пользователя"""
        try:
            user_id = input("\nВведите ID пользователя для удаления: ").strip()
            if not user_id.isdigit():
                print("❌ ID должен быть числом!")
                return

            confirm = input(f"Вы уверены, что хотите удалить пользователя {user_id}? (y/N): ").strip().lower()
            if confirm != 'y':
                print("❌ Удаление отменено")
                return

            success = await self.user_service.delete_user(int(user_id))
            if success:
                print(f"\n✅ Пользователь {user_id} удален")
            else:
                print(f"\n❌ Не удалось удалить пользователя {user_id}")

        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

    async def manage_authors(self):
        """Управление авторами"""
        while True:
            print("\n" + "-" * 40)
            print("УПРАВЛЕНИЕ АВТОРАМИ")
            print("-" * 40)
            print("1. Показать всех авторов")
            print("2. Добавить автора")
            print("3. Найти автора по ID")
            print("4. Обновить автора")
            print("5. Удалить автора")
            print("6. Назад")

            choice = input("\nВыберите действие (1-6): ").strip()

            if choice == "1":
                await self.show_all_authors()
            elif choice == "2":
                await self.create_author()
            elif choice == "3":
                await self.get_author_by_id()
            elif choice == "4":
                await self.update_author()
            elif choice == "5":
                await self.delete_author()
            elif choice == "6":
                break
            else:
                print("\n❌ Неверный выбор!")

    async def show_all_authors(self):
        """Показать всех авторов"""
        try:
            authors = await self.author_service.get_author()
            if not authors:
                print("\n📭 Нет авторов в базе")
                return

            print("\n" + "=" * 60)
            print("СПИСОК АВТОРОВ")
            print("=" * 60)
            for author in authors:
                print(f"ID: {author.id}")
                print(f"Фамилия: {author.second_name}")
                print(f"Имя: {author.first_name}")
                print(f"Отчество: {author.third_name or '-'}")
                print(f"Дата рождения: {author.birth_date or '-'}")
                print("-" * 40)
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

    async def create_author(self):
        """Создать нового автора"""
        try:
            print("\nСОЗДАНИЕ НОВОГО АВТОРА")
            print("-" * 30)

            first_name = input("Имя: ").strip()
            second_name = input("Фамилия: ").strip()
            third_name = input("Отчество (опционально): ").strip() or None
            birth_date = input("Дата рождения (ГГГГ-ММ-ДД, опционально): ").strip() or None

            author_data = AuthorFull(
                first_name=first_name,
                second_name=second_name,
                third_name=third_name,
                birth_date=birth_date
            )

            author = await self.author_service.create_author(author_data)
            print(f"\n✅ Автор создан! ID: {author.id}")

        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

    async def get_author_by_id(self):
        """Найти автора по ID"""
        try:
            author_id = input("\nВведите ID автора: ").strip()
            if not author_id.isdigit():
                print("❌ ID должен быть числом!")
                return

            author = await self.author_service.get_author(int(author_id))

            if author:
                print(f"\n✅ Найден автор:")
                print(f"ID: {author.id}")
                print(f"Фамилия: {author.second_name}")
                print(f"Имя: {author.first_name}")
                print(f"Отчество: {author.third_name or '-'}")
                print(f"Дата рождения: {author.birth_date or '-'}")
            else:
                print(f"\n❌ Автор с ID {author_id} не найден")

        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

    async def update_author(self):
        """Обновить данные автора"""
        try:
            author_id = input("\nВведите ID автора для обновления: ").strip()
            if not author_id.isdigit():
                print("❌ ID должен быть числом!")
                return

            author = await self.author_service.get_author(int(author_id))

            if not author:
                print(f"\n❌ Автор с ID {author_id} не найден")
                return

            print(f"\nТекущие данные автора:")
            print(f"Фамилия: {author.second_name}")
            print(f"Имя: {author.first_name}")
            print(f"Отчество: {author.third_name or '-'}")
            print(f"Дата рождения: {author.birth_date or '-'}")

            print("\nВведите новые данные (оставьте пустым, чтобы не менять):")
            first_name = input("Имя: ").strip() or author.first_name
            second_name = input("Фамилия: ").strip() or author.second_name
            third_name = input("Отчество: ").strip() or author.third_name
            birth_date = input("Дата рождения (ГГГГ-ММ-ДД): ").strip() or author.birth_date

            update_data = AuthorFull(
                first_name=first_name,
                second_name=second_name,
                third_name=third_name,
                birth_date=birth_date
            )

            updated_author = await self.author_service.update_author(int(author_id), update_data)
            print(f"\n✅ Данные автора обновлены!")

        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

    async def delete_author(self):
        """Удалить автора"""
        try:
            author_id = input("\nВведите ID автора для удаления: ").strip()
            if not author_id.isdigit():
                print("❌ ID должен быть числом!")
                return

            confirm = input(f"Вы уверены, что хотите удалить автора {author_id}? (y/N): ").strip().lower()
            if confirm != 'y':
                print("❌ Удаление отменено")
                return

            success = await self.author_service.delete_author(int(author_id))
            if success:
                print(f"\n✅ Автор {author_id} удален")
            else:
                print(f"\n❌ Не удалось удалить автора {author_id}")

        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

    async def manage_books(self):
        """Управление книгами"""
        while True:
            print("\n" + "-" * 40)
            print("УПРАВЛЕНИЕ КНИГАМИ")
            print("-" * 40)
            print("1. Показать все книги")
            print("2. Добавить книгу")
            print("3. Найти книгу по ID")
            print("4. Обновить книгу")
            print("5. Удалить книгу")
            print("6. Назад")

            choice = input("\nВыберите действие (1-6): ").strip()

            if choice == "1":
                await self.show_all_books()
            elif choice == "2":
                await self.create_book()
            elif choice == "3":
                await self.get_book_by_id()
            elif choice == "4":
                await self.update_book()
            elif choice == "5":
                await self.delete_book()
            elif choice == "6":
                break
            else:
                print("\n❌ Неверный выбор!")

    async def show_all_books(self):
        """Показать все книги"""
        try:
            books = await self.book_service.get_book()
            if not books:
                print("\n📭 Нет книг в базе")
                return

            print("\n" + "=" * 80)
            print("СПИСОК КНИГ")
            print("=" * 80)
            for book in books:
                print(f"ID: {book.id}")
                print(f"Название: {book.title}")
                print(f"Автор ID: {book.author}")
                print(f"Год издания: {book.publication_year or '-'}")
                print(f"Жанр ID: {book.genre or '-'}")
                print(f"ISBN: {book.isbn or '-'}")
                print(f"Количество страниц: {book.page_count or '-'}")
                print(f"Зарезервирована: {'Да' if book.reserved_by else 'Нет'}")
                print("-" * 80)
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

    async def create_book(self):
        """Создать новую книгу"""
        try:
            print("\nСОЗДАНИЕ НОВОЙ КНИГИ")
            print("-" * 30)

            title = input("Название: ").strip()
            author_id = input("ID автора: ").strip()
            publication_year = input("Год издания (опционально): ").strip()
            genre_id = input("ID жанра (опционально): ").strip()
            isbn = input("ISBN (опционально): ").strip()
            page_count = input("Количество страниц (опционально): ").strip()

            book_data = BookFull(
                title=title,
                author=int(author_id) if author_id.isdigit() else None,
                publication_year=int(publication_year) if publication_year.isdigit() else None,
                genre=int(genre_id) if genre_id.isdigit() else None,
                isbn=isbn or None,
                page_count=int(page_count) if page_count.isdigit() else None
            )

            book = await self.book_service.create_book(book_data)
            print(f"\n✅ Книга создана! ID: {book.id}")

        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

    async def get_book_by_id(self):
        """Найти книгу по ID"""
        try:
            book_id = input("\nВведите ID книги: ").strip()
            if not book_id.isdigit():
                print("❌ ID должен быть числом!")
                return

            book = await self.book_service.get_book(int(book_id))

            if book:
                print(f"\n✅ Найдена книга:")
                print(f"ID: {book.id}")
                print(f"Название: {book.title}")
                print(f"Автор ID: {book.author}")
                print(f"Год издания: {book.publication_year or '-'}")
                print(f"Жанр ID: {book.genre or '-'}")
                print(f"ISBN: {book.isbn or '-'}")
                print(f"Количество страниц: {book.page_count or '-'}")
                print(f"Зарезервирована: {'Да' if book.reserved_by else 'Нет'}")
            else:
                print(f"\n❌ Книга с ID {book_id} не найдена")

        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

    async def update_book(self):
        """Обновить данные книги"""
        try:
            book_id = input("\nВведите ID книги для обновления: ").strip()
            if not book_id.isdigit():
                print("❌ ID должен быть числом!")
                return

            book = await self.book_service.get_book(int(book_id))

            if not book:
                print(f"\n❌ Книга с ID {book_id} не найдена")
                return

            print(f"\nТекущие данные книги '{book.title}':")
            print(f"Автор ID: {book.author}")
            print(f"Год издания: {book.publication_year or '-'}")
            print(f"Жанр ID: {book.genre or '-'}")
            print(f"ISBN: {book.isbn or '-'}")
            print(f"Количество страниц: {book.page_count or '-'}")

            print("\nВведите новые данные (оставьте пустым, чтобы не менять):")
            title = input("Название: ").strip() or book.title
            author_id = input("ID автора: ").strip() or str(book.author)
            publication_year = input("Год издания: ").strip() or str(book.publication_year or '')
            genre_id = input("ID жанра: ").strip() or str(book.genre or '')
            isbn = input("ISBN: ").strip() or book.isbn
            page_count = input("Количество страниц: ").strip() or str(book.page_count or '')

            update_data = BookFull(
                title=title,
                author=int(author_id) if author_id.isdigit() else None,
                publication_year=int(publication_year) if publication_year.isdigit() else None,
                genre=int(genre_id) if genre_id.isdigit() else None,
                isbn=isbn or None,
                page_count=int(page_count) if page_count.isdigit() else None
            )

            updated_book = await self.book_service.update_book(int(book_id), update_data)
            print(f"\n✅ Данные книги обновлены!")

        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

    async def delete_book(self):
        """Удалить книгу"""
        try:
            book_id = input("\nВведите ID книги для удаления: ").strip()
            if not book_id.isdigit():
                print("❌ ID должен быть числом!")
                return

            confirm = input(f"Вы уверены, что хотите удалить книгу {book_id}? (y/N): ").strip().lower()
            if confirm != 'y':
                print("❌ Удаление отменено")
                return

            success = await self.book_service.delete_book(int(book_id))
            if success:
                print(f"\n✅ Книга {book_id} удалена")
            else:
                print(f"\n❌ Не удалось удалить книгу {book_id}")

        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

    async def manage_genres(self):
        """Управление жанрами"""
        while True:
            print("\n" + "-" * 40)
            print("УПРАВЛЕНИЕ ЖАНРАМИ")
            print("-" * 40)
            print("1. Показать все жанры")
            print("2. Добавить жанр")
            print("3. Найти жанр по ID")
            print("4. Обновить жанр")
            print("5. Удалить жанр")
            print("6. Назад")

            choice = input("\nВыберите действие (1-6): ").strip()

            if choice == "1":
                await self.show_all_genres()
            elif choice == "2":
                await self.create_genre()
            elif choice == "3":
                await self.get_genre_by_id()
            elif choice == "4":
                await self.update_genre()
            elif choice == "5":
                await self.delete_genre()
            elif choice == "6":
                break
            else:
                print("\n❌ Неверный выбор!")

    async def show_all_genres(self):
        """Показать все жанры"""
        try:
            genres = await self.genre_service.get_genre()
            if not genres:
                print("\n📭 Нет жанров в базе")
                return

            print("\n" + "=" * 40)
            print("СПИСОК ЖАНРОВ")
            print("=" * 40)
            for genre in genres:
                print(f"ID: {genre.id}")
                print(f"Название: {genre.name}")
                print("-" * 40)
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

    async def create_genre(self):
        """Создать новый жанр"""
        try:
            print("\nСОЗДАНИЕ НОВОГО ЖАНРА")
            print("-" * 30)

            name = input("Название жанра: ").strip()

            genre_data = GenreDefault(name=name)
            genre = await self.genre_service.create_genre(genre_data)
            print(f"\n✅ Жанр создан! ID: {genre.id}")

        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

    async def get_genre_by_id(self):
        """Найти жанр по ID"""
        try:
            genre_id = input("\nВведите ID жанра: ").strip()
            if not genre_id.isdigit():
                print("❌ ID должен быть числом!")
                return

            genre = await self.genre_service.get_genre(int(genre_id))

            if genre:
                print(f"\n✅ Найден жанр:")
                print(f"ID: {genre.id}")
                print(f"Название: {genre.name}")
            else:
                print(f"\n❌ Жанр с ID {genre_id} не найден")

        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

    async def update_genre(self):
        """Обновить данные жанра"""
        try:
            genre_id = input("\nВведите ID жанра для обновления: ").strip()
            if not genre_id.isdigit():
                print("❌ ID должен быть числом!")
                return

            genre = await self.genre_service.get_genre(int(genre_id))

            if not genre:
                print(f"\n❌ Жанр с ID {genre_id} не найден")
                return

            print(f"\nТекущее название жанра: {genre.name}")
            new_name = input("\nВведите новое название: ").strip()

            if new_name:
                update_data = GenreDefault(name=new_name)
                updated_genre = await self.genre_service.update_genre(int(genre_id), update_data)
                print(f"\n✅ Название жанра обновлено!")
            else:
                print("\n⚠️  Название не изменено")

        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

    async def delete_genre(self):
        """Удалить жанр"""
        try:
            genre_id = input("\nВведите ID жанра для удаления: ").strip()
            if not genre_id.isdigit():
                print("❌ ID должен быть числом!")
                return

            confirm = input(f"Вы уверены, что хотите удалить жанр {genre_id}? (y/N): ").strip().lower()
            if confirm != 'y':
                print("❌ Удаление отменено")
                return

            success = await self.genre_service.delete_genre(int(genre_id))
            if success:
                print(f"\n✅ Жанр {genre_id} удален")
            else:
                print(f"\n❌ Не удалось удалить жанр {genre_id}")

        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

    async def manage_bookings(self):
        """Управление бронированиями"""
        while True:
            print("\n" + "-" * 40)
            print("УПРАВЛЕНИЕ БРОНИРОВАНИЯМИ")
            print("-" * 40)
            print("1. Показать все бронирования")
            print("2. Показать бронирования пользователя")
            print("3. Добавить бронирование")
            print("4. Найти бронирование по ID")
            print("5. Завершить бронирование (возврат книги)")
            print("6. Удалить бронирование")
            print("7. Назад")

            choice = input("\nВыберите действие (1-7): ").strip()

            if choice == "1":
                await self.show_all_bookings()
            elif choice == "2":
                await self.show_user_bookings()
            elif choice == "3":
                await self.create_booking()
            elif choice == "4":
                await self.get_booking_by_id()
            elif choice == "5":
                await self.complete_booking()
            elif choice == "6":
                await self.delete_booking()
            elif choice == "7":
                break
            else:
                print("\n❌ Неверный выбор!")

    async def show_all_bookings(self):
        """Показать все бронирования"""
        try:
            bookings = await self.booking_service.get_booking()
            if not bookings:
                print("\n📭 Нет активных бронирований")
                return

            print("\n" + "=" * 80)
            print("СПИСОК БРОНИРОВАНИЙ")
            print("=" * 80)
            for booking in bookings:
                print(f"ID: {booking.id}")
                print(f"ID пользователя: {booking.user_id}")
                print(f"ID книги: {booking.book_id}")
                print(f"Дата взятия: {booking.take_date}")
                print(f"Дата возврата: {booking.end_date or 'Еще не возвращена'}")
                print(f"Статус: {'Завершено' if booking.end_date else 'Активно'}")
                print("-" * 80)
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

    async def show_user_bookings(self):
        """Показать бронирования конкретного пользователя"""
        try:
            user_id = input("\nВведите ID пользователя: ").strip()
            if not user_id.isdigit():
                print("❌ ID должен быть числом!")
                return

            bookings = await self.booking_service.get_booking(user_id=int(user_id))
            if not bookings:
                print(f"\n📭 У пользователя {user_id} нет бронирований")
                return

            print(f"\nБронирования пользователя {user_id}:")
            print("=" * 60)
            for booking in bookings:
                print(f"ID бронирования: {booking.id}")
                print(f"ID книги: {booking.book_id}")
                print(f"Дата взятия: {booking.take_date}")
                print(f"Дата возврата: {booking.end_date or 'Еще не возвращена'}")
                print(f"Статус: {'Завершено' if booking.end_date else 'Активно'}")
                print("-" * 60)
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

    async def create_booking(self):
        """Создать новое бронирование"""
        try:
            print("\nСОЗДАНИЕ НОВОГО БРОНИРОВАНИЯ")
            print("-" * 30)

            user_id = input("ID пользователя: ").strip()
            book_id = input("ID книги: ").strip()

            if not user_id.isdigit() or not book_id.isdigit():
                print("❌ ID должны быть числами!")
                return

            booking_data = BookingDefault(
                user_id=int(user_id),
                book_id=int(book_id)
            )

            booking = await self.booking_service.create_booking(booking_data)
            print(f"\n✅ Бронирование создано! ID: {booking.id}")

        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

    async def get_booking_by_id(self):
        """Найти бронирование по ID"""
        try:
            booking_id = input("\nВведите ID бронирования: ").strip()
            if not booking_id.isdigit():
                print("❌ ID должен быть числом!")
                return

            booking = await self.booking_service.get_booking(int(booking_id))

            if booking:
                print(f"\n✅ Найдено бронирование:")
                print(f"ID: {booking.id}")
                print(f"ID пользователя: {booking.user_id}")
                print(f"ID книги: {booking.book_id}")
                print(f"Дата взятия: {booking.take_date}")
                print(f"Дата возврата: {booking.end_date or 'Еще не возвращена'}")
                print(f"Статус: {'Завершено' if booking.end_date else 'Активно'}")
            else:
                print(f"\n❌ Бронирование с ID {booking_id} не найдено")

        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

    async def complete_booking(self):
        """Завершить бронирование (вернуть книгу)"""
        try:
            booking_id = input("\nВведите ID бронирования для завершения: ").strip()
            if not booking_id.isdigit():
                print("❌ ID должен быть числом!")
                return

            confirm = input(f"Вы уверены, что хотите завершить бронирование {booking_id}? (y/N): ").strip().lower()
            if confirm != 'y':
                print("❌ Отменено")
                return

            booking = await self.booking_service.complete_booking(int(booking_id))
            print(f"\n✅ Бронирование {booking_id} завершено! Книга возвращена.")

        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

    async def delete_booking(self):
        """Удалить бронирование"""
        try:
            booking_id = input("\nВведите ID бронирования для удаления: ").strip()
            if not booking_id.isdigit():
                print("❌ ID должен быть числом!")
                return

            confirm = input(f"Вы уверены, что хотите удалить бронирование {booking_id}? (y/N): ").strip().lower()
            if confirm != 'y':
                print("❌ Удаление отменено")
                return

            success = await self.booking_service.delete_booking(int(booking_id))
            if success:
                print(f"\n✅ Бронирование {booking_id} удалено")
            else:
                print(f"\n❌ Не удалось удалить бронирование {booking_id}")

        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

    async def search_records(self):
        """Поиск записей по различным критериям"""
        print("\n" + "=" * 50)
        print("ПОИСК ЗАПИСЕЙ")
        print("=" * 50)
        print("1. Поиск книг по названию")
        print("2. Поиск книг по автору")
        print("3. Поиск авторов по имени")
        print("4. Поиск пользователей по email")
        print("5. Назад")

        choice = input("\nВыберите тип поиска (1-5): ").strip()

        if choice == "1":
            await self.search_books_by_title()
        elif choice == "2":
            await self.search_books_by_author()
        elif choice == "3":
            await self.search_authors_by_name()
        elif choice == "4":
            await self.search_users_by_email()
        elif choice == "5":
            return
        else:
            print("\n❌ Неверный выбор!")

    async def search_books_by_title(self):
        """Поиск книг по названию"""
        try:
            search_term = input("\nВведите часть названия книги: ").strip()

            books = await self.book_service.get_book()
            if books:
                filtered_books = [book for book in books if search_term.lower() in book.title.lower()]

                if filtered_books:
                    print(f"\nНайдено {len(filtered_books)} книг:")
                    print("-" * 60)
                    for book in filtered_books:
                        print(f"ID: {book.id}, Название: {book.title}, ISBN: {book.isbn or '-'}")
                else:
                    print(f"\n📭 Книги по запросу '{search_term}' не найдены")
            else:
                print("\n📭 В базе нет книг")

        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

    async def search_books_by_author(self):
        """Поиск книг по автору"""
        try:
            author_id = input("\nВведите ID автора: ").strip()
            if not author_id.isdigit():
                print("❌ ID должен быть числом!")
                return

            books = await self.book_service.get_book()
            if books:
                filtered_books = [book for book in books if book.author == int(author_id)]

                if filtered_books:
                    print(f"\nНайдено {len(filtered_books)} книг автора {author_id}:")
                    print("-" * 60)
                    for book in filtered_books:
                        print(f"ID: {book.id}, Название: {book.title}, Год: {book.publication_year or '-'}")
                else:
                    print(f"\n📭 У автора {author_id} нет книг в базе")
            else:
                print("\n📭 В базе нет книг")

        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

    async def search_authors_by_name(self):
        """Поиск авторов по имени"""
        try:
            search_term = input("\nВведите часть имени или фамилии автора: ").strip()

            authors = await self.author_service.get_author()
            if authors:
                filtered_authors = [
                    author for author in authors
                    if search_term.lower() in author.first_name.lower() or
                       search_term.lower() in author.second_name.lower()
                ]

                if filtered_authors:
                    print(f"\nНайдено {len(filtered_authors)} авторов:")
                    print("-" * 60)
                    for author in filtered_authors:
                        print(
                            f"ID: {author.id}, Имя: {author.first_name} {author.second_name}, Дата рождения: {author.birth_date or '-'}")
                else:
                    print(f"\n📭 Авторы по запросу '{search_term}' не найдены")
            else:
                print("\n📭 В базе нет авторов")

        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

    async def search_users_by_email(self):
        """Поиск пользователей по email"""
        try:
            search_term = input("\nВведите часть email: ").strip()

            users = await self.user_service.get_all()
            if users:
                filtered_users = [user for user in users if search_term.lower() in user.email.lower()]

                if filtered_users:
                    print(f"\nНайдено {len(filtered_users)} пользователей:")
                    print("-" * 60)
                    for user in filtered_users:
                        print(f"ID: {user.id}, Email: {user.email}, Имя: {user.username or '-'}")
                else:
                    print(f"\n📭 Пользователи по запросу '{search_term}' не найдены")
            else:
                print("\n📭 В базе нет пользователей")

        except Exception as e:
            print(f"\n❌ Ошибка: {e}")


async def main():
    """Главная функция CLI"""
    cli = AdminCLI()

    try:
        await cli.initialize_services()

        if await cli.authenticate():
            await cli.show_main_menu()
        else:
            print("\n❌ Не удалось войти. Проверьте логин и пароль.")

    except KeyboardInterrupt:
        print("\n\n👋 Программа завершена пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
    finally:
        print("\nСпасибо за использование административной консоли!")


if __name__ == "__main__":
    asyncio.run(main())