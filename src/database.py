import sqlite3
from typing import Optional, List, Dict, Any


class DatabaseRepository:
    """
    Репозиторий для работы с базой данных SQLite для хранения комментариев.
    """

    MAX_NAME_LENGTH = 256
    MAX_MESSAGE_LENGTH = 8096

    def __init__(self, db_path: str = ":memory:"):
        """
        Инициализация репозитория.

        :param db_path: Путь к файлу базы данных SQLite или ':memory:' для работы в ОЗУ.
        """
        self.db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None
        self._connect()
        self._create_table()

    def _connect(self) -> None:
        """Создание подключения к базе данных."""
        self._connection = sqlite3.connect(self.db_path)
        # Позволяет получать строки как словари (доступ по именам колонок)
        self._connection.row_factory = sqlite3.Row

    @property
    def connection(self) -> sqlite3.Connection:
        """Возвращает активное подключение к базе данных."""
        if self._connection is None:
            self._connect()
        return self._connection

    def _create_table(self) -> None:
        """Создание таблицы comments, если она еще не создана."""
        query = """
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            message TEXT NOT NULL
        );
        """
        with self.connection:
            self.connection.execute(query)

    def _validate_comment_id(self, comment_id: int) -> None:
        """Проверка валидности идентификатора комментария."""
        if not isinstance(comment_id, int) or isinstance(comment_id, bool):
            raise TypeError(f"ID комментария должен быть целым числом (int), получено: {type(comment_id).__name__}")

    def _validate_name(self, name: str) -> None:
        """Проверка валидности имени пользователя."""
        if not isinstance(name, str):
            raise TypeError(f"Имя пользователя должно быть строкой (str), получено: {type(name).__name__}")
        if not name.strip():
            raise ValueError("Имя пользователя не может быть пустым.")
        if len(name) > self.MAX_NAME_LENGTH:
            raise ValueError(f"Длина имени превышает {self.MAX_NAME_LENGTH} символов (получено: {len(name)}).")

    def _validate_message(self, message: str) -> None:
        """Проверка валидности текста сообщения."""
        if not isinstance(message, str):
            raise TypeError(f"Сообщение должно быть строкой (str), получено: {type(message).__name__}")
        if not message.strip():
            raise ValueError("Сообщение не может быть пустым.")
        if len(message) > self.MAX_MESSAGE_LENGTH:
            raise ValueError(f"Длина сообщения превышает {self.MAX_MESSAGE_LENGTH} символов (получено: {len(message)}).")

    def add(self, comment_id: int, username: str, message: str) -> bool:
        """
        Добавление новой записи в таблицу comments.

        :param comment_id: Уникальный целочисленный идентификатор сообщения.
        :param username: Логин автора (до 256 символов).
        :param message: Текст сообщения с HTML-разметкой (до 8096 символов).
        :return: True при успешной вставке.
        :raises TypeError: При несоответствии типов аргументов.
        :raises ValueError: При нарушении ограничений по длине строк.
        :raises sqlite3.IntegrityError: При попытке вставить уже существующий ID.
        """
        self._validate_comment_id(comment_id)
        self._validate_name(username)
        self._validate_message(message)

        query = "INSERT INTO comments (id, name, message) VALUES (?, ?, ?);"
        with self.connection:
            self.connection.execute(query, (comment_id, username, message))
        return True

    def get_by_id(self, comment_id: int) -> Optional[Dict[str, Any]]:
        """
        Получение одной записи по заданному ID.

        :param comment_id: Идентификатор комментария.
        :return: Словарь с данными комментария или None, если запись не найдена.
        :raises TypeError: Если comment_id не является целым числом.
        """
        self._validate_comment_id(comment_id)

        query = "SELECT id, name, message FROM comments WHERE id = ?;"
        cursor = self.connection.execute(query, (comment_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return dict(row)

    def get_by_name(self, username: str) -> List[Dict[str, Any]]:
        """
        Получение списка всех записей, оставленных пользователем с конкретным именем.

        :param username: Логин автора.
        :return: Список словарей с комментариями пользователя.
        :raises TypeError: Если username не является строкой.
        """
        if not isinstance(username, str):
            raise TypeError(f"Имя пользователя должно быть строкой (str), получено: {type(username).__name__}")

        query = "SELECT id, name, message FROM comments WHERE name = ? ORDER BY id ASC;"
        cursor = self.connection.execute(query, (username,))
        return [dict(row) for row in cursor.fetchall()]

    def update(self, comment_id: int, new_message: str) -> bool:
        """
        Изменение поля message у существующей записи по заданному ID.

        :param comment_id: Идентификатор комментария.
        :param new_message: Новый текст сообщения (до 8096 символов).
        :return: True при успешном обновлении.
        :raises TypeError: При некорректном типе данных.
        :raises ValueError: Если запись с таким ID не найдена или длина строки недопустима.
        """
        self._validate_comment_id(comment_id)
        self._validate_message(new_message)

        query = "UPDATE comments SET message = ? WHERE id = ?;"
        with self.connection:
            cursor = self.connection.execute(query, (new_message, comment_id))
            if cursor.rowcount == 0:
                raise ValueError(f"Запись с ID {comment_id} не найдена для обновления.")
        return True

    def delete(self, comment_id: int) -> bool:
        """
        Удаление строки по comment_id.

        :param comment_id: Идентификатор комментария.
        :return: True, если запись была найдена и удалена, иначе False.
        :raises TypeError: Если comment_id не является целым числом.
        """
        self._validate_comment_id(comment_id)

        query = "DELETE FROM comments WHERE id = ?;"
        with self.connection:
            cursor = self.connection.execute(query, (comment_id,))
            return cursor.rowcount > 0

    def close(self) -> None:
        """Закрытие подключения к базе данных."""
        if self._connection:
            self._connection.close()
            self._connection = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

