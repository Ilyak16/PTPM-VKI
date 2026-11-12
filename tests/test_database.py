import sqlite3
import unittest
from src.database import DatabaseRepository


class TestDatabaseRepository(unittest.TestCase):
    def setUp(self):
        self.repo = DatabaseRepository(":memory:")

    def tearDown(self):
        self.repo.close()

    def test_add_success(self):
        result = self.repo.add(1, "ivan_dev", "Привет, мир!")
        self.assertTrue(result)

        record = self.repo.get_by_id(1)
        self.assertIsNotNone(record)
        self.assertEqual(record["id"], 1)
        self.assertEqual(record["name"], "ivan_dev")
        self.assertEqual(record["message"], "Привет, мир!")

    def test_add_duplicate_id_raises_integrity_error(self):
        self.repo.add(10, "alice", "Первое сообщение")
        with self.assertRaises(sqlite3.IntegrityError):
            self.repo.add(10, "bob", "Второе сообщение с тем же ID")

    def test_add_name_too_long_raises_value_error(self):
        long_name = "a" * (DatabaseRepository.MAX_NAME_LENGTH + 1)
        with self.assertRaises(ValueError):
            self.repo.add(2, long_name, "Валидное сообщение")

    def test_add_message_too_long_raises_value_error(self):
        long_message = "x" * (DatabaseRepository.MAX_MESSAGE_LENGTH + 1)
        with self.assertRaises(ValueError):
            self.repo.add(3, "valid_user", long_message)

    def test_add_invalid_types_raise_type_error(self):
        # ID не целое число
        with self.assertRaises(TypeError):
            self.repo.add("not_an_int", "user", "message")  # type: ignore

        # ID является bool (так как в Python bool - подкласс int)
        with self.assertRaises(TypeError):
            self.repo.add(True, "user", "message")  # type: ignore

        # Имя не строка
        with self.assertRaises(TypeError):
            self.repo.add(4, 12345, "message")  # type: ignore

        # Сообщение не строка
        with self.assertRaises(TypeError):
            self.repo.add(5, "user", ["not_a_string"])  # type: ignore

    # ==========================================
    # Тесты для метода: get_by_id
    # ==========================================

    def test_get_by_id_success(self):
        """Тест 1 (get_by_id): Успешное получение существующей записи по ID."""
        self.repo.add(42, "tester", "Тестовый текст сообщения")
        record = self.repo.get_by_id(42)

        self.assertIsInstance(record, dict)
        self.assertEqual(record["id"], 42)
        self.assertEqual(record["name"], "tester")
        self.assertEqual(record["message"], "Тестовый текст сообщения")

    def test_get_by_id_not_found_returns_none(self):
        """Тест 2 (get_by_id): Запрос несуществующего ID возвращает None."""
        record = self.repo.get_by_id(99999)
        self.assertIsNone(record)

    def test_get_by_id_invalid_type_raises_type_error(self):
        """Тест 3 (get_by_id): Передача нечислового идентификатора вызывает TypeError."""
        with self.assertRaises(TypeError):
            self.repo.get_by_id("abc")  # type: ignore

    # ==========================================
    # Тесты для метода: get_by_name
    # ==========================================

    def test_get_by_name_success_multiple_records(self):
        """Тест 1 (get_by_name): Успешное получение списка всех сообщений конкретного автора."""
        self.repo.add(1, "alex", "Сообщение 1 от alex")
        self.repo.add(2, "john", "Сообщение от john")
        self.repo.add(3, "alex", "Сообщение 2 от alex")

        alex_records = self.repo.get_by_name("alex")
        self.assertEqual(len(alex_records), 2)
        self.assertEqual([r["id"] for r in alex_records], [1, 3])
        self.assertTrue(all(r["name"] == "alex" for r in alex_records))

    def test_get_by_name_empty_list_for_unknown_user(self):
        """Тест 2 (get_by_name): Для пользователя без сообщений возвращается пустой список."""
        records = self.repo.get_by_name("unknown_user")
        self.assertIsInstance(records, list)
        self.assertEqual(len(records), 0)

    def test_get_by_name_invalid_type_raises_type_error(self):
        """Тест 3 (get_by_name): Нестроковый тип имени вызывает TypeError."""
        with self.assertRaises(TypeError):
            self.repo.get_by_name(123)  # type: ignore

    # ==========================================
    # Тесты для метода: update
    # ==========================================

    def test_update_success(self):
        """Тест 1 (update): Успешное обновление поля message у существующей записи."""
        self.repo.add(100, "moderator", "Старый текст сообщения")
        new_text = "<b>Обновленный</b> текст сообщения с HTML-разметкой"

        update_result = self.repo.update(100, new_text)
        self.assertTrue(update_result)

        updated_record = self.repo.get_by_id(100)
        self.assertEqual(updated_record["message"], new_text)
        self.assertEqual(updated_record["name"], "moderator")

    def test_update_non_existent_id_raises_value_error(self):
        """Тест 2 (update): Попытка обновить несуществующий ID вызывает ValueError."""
        with self.assertRaises(ValueError):
            self.repo.update(99999, "Новый текст для несуществующего поста")

    def test_update_message_too_long_raises_value_error(self):
        """Тест 3 (update): Превышение максимальной длины сообщения при обновлении вызывает ValueError."""
        self.repo.add(101, "writer", "Обычное сообщение")
        too_long = "z" * (DatabaseRepository.MAX_MESSAGE_LENGTH + 1)
        with self.assertRaises(ValueError):
            self.repo.update(101, too_long)

    # ==========================================
    # Тесты для метода: delete
    # ==========================================

    def test_delete_success(self):
        """Тест 1 (delete): Успешное удаление существующей записи по ID."""
        self.repo.add(77, "to_delete", "Это сообщение будет удалено")

        # Удаляем запись
        result = self.repo.delete(77)
        self.assertTrue(result)

        # Проверяем, что запись больше не существует
        self.assertIsNone(self.repo.get_by_id(77))

    def test_delete_non_existent_id_returns_false(self):
        """Тест 2 (delete): Попытка удалить несуществующий ID возвращает False."""
        result = self.repo.delete(99999)
        self.assertFalse(result)

    def test_delete_invalid_type_raises_type_error(self):
        """Тест 3 (delete): Передача нечислового идентификатора при удалении вызывает TypeError."""
        with self.assertRaises(TypeError):
            self.repo.delete("string_id")  # type: ignore


if __name__ == "__main__":
    unittest.main()

