import os
import sqlite3
import unittest
from unittest.mock import patch, MagicMock
from src.database import DatabaseRepository
from src.parser import ForumParser


class TestForumParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Загрузка HTML-слепка страницы форума из фикстуры."""
        fixture_path = os.path.join(os.path.dirname(__file__), "fixtures", "sample_forum.html")
        with open(fixture_path, "r", encoding="utf-8") as f:
            cls.sample_html = f.read()

    def setUp(self):
        """Создание экземпляра парсера перед каждым тестом."""
        self.parser = ForumParser()

    # ==========================================
    # Тест-кейсы извлечения данных из фикстуры
    # ==========================================

    def test_parse_html_from_fixture_extracts_correct_data(self):
        """Тест 1: Корректное извлечение ID, авторов и сообщений из HTML-фикстуры."""
        data = self.parser.parse_html(self.sample_html)

        # В фикстуре ровно 4 валидных сообщения (невалидные блоки без ID или автора отсеиваются)
        self.assertEqual(len(data), 4)

        # Проверяем первое сообщение (id="comment-101")
        self.assertEqual(data[0]["id"], 101)
        self.assertEqual(data[0]["name"], "AlexDev")
        self.assertIn("<b>ColorOS 17</b>", data[0]["message"])

        # Проверяем второе сообщение (id="comment-102")
        self.assertEqual(data[1]["id"], 102)
        self.assertEqual(data[1]["name"], "Coder99")
        self.assertIn("OnePlus 12", data[1]["message"])

        # Проверяем третье сообщение (id="comment-103")
        self.assertEqual(data[2]["id"], 103)
        self.assertEqual(data[2]["name"], "PythonLover")
        self.assertIn("realme GT 6", data[2]["message"])

        # Проверяем четвертое сообщение (от AlexDev, id="comment-104")
        self.assertEqual(data[3]["id"], 104)
        self.assertEqual(data[3]["name"], "AlexDev")
        self.assertEqual(data[3]["message"], "Для realme обещали до конца месяца.")

    def test_parse_html_empty_or_whitespace_returns_empty_list(self):
        """Тест 2: Разбор пустой строки или HTML без постов возвращает пустой список."""
        self.assertEqual(self.parser.parse_html(""), [])
        self.assertEqual(self.parser.parse_html("   \n\t  "), [])
        self.assertEqual(self.parser.parse_html("<html><body><div>Нет постов</div></body></html>"), [])
    # ==========================================

    def test_save_to_db_success(self):
        """Тест 3: Успешное сохранение спарсенных данных в DatabaseRepository."""
        repo = DatabaseRepository(":memory:")
        parsed_data = self.parser.parse_html(self.sample_html)

        saved_count = self.parser.save_to_db(parsed_data, repo)
        self.assertEqual(saved_count, 4)

        # Проверяем сохраненные данные через репозиторий
        post_101 = repo.get_by_id(101)
        self.assertIsNotNone(post_101)
        self.assertEqual(post_101["name"], "AlexDev")

        # Проверяем поиск всех постов автора AlexDev
        alex_posts = repo.get_by_name("AlexDev")
        self.assertEqual(len(alex_posts), 2)
        self.assertEqual([p["id"] for p in alex_posts], [101, 104])

        repo.close()

    def test_save_to_db_duplicate_handling(self):
        """Тест 4: Обработка дубликатов при сохранении в базу данных."""
        repo = DatabaseRepository(":memory:")
        data = [
            {"id": 1, "name": "user1", "message": "msg 1"},
            {"id": 1, "name": "user1", "message": "duplicate msg"}
        ]

        # При ignore_duplicates=True второе сообщение пропускается, сохраняется только 1
        count = self.parser.save_to_db(data, repo, ignore_duplicates=True)
        self.assertEqual(count, 1)

        # При ignore_duplicates=False выбрасывается исключение IntegrityError
        with self.assertRaises(sqlite3.IntegrityError):
            self.parser.save_to_db(data, repo, ignore_duplicates=False)

        repo.close()

    # ==========================================

    @patch("requests.get")
    def test_parse_page_uses_headers_and_user_agent(self, mock_get):
        """Тест 5: parse_page отправляет запрос с правильными заголовками (включая User-Agent)."""
        mock_response = MagicMock()
        mock_response.text = self.sample_html
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        test_url = "https://example.com/forum/topic/42"
        results = self.parser.parse_page(test_url)

        # Проверяем, что requests.get был вызван с нужным URL и заголовками
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], test_url)
        self.assertIn("headers", kwargs)
        self.assertIn("User-Agent", kwargs["headers"])
        self.assertIn("Mozilla", kwargs["headers"]["User-Agent"])

        # Проверяем результат парсинга
        self.assertEqual(len(results), 4)


if __name__ == "__main__":
    unittest.main()

