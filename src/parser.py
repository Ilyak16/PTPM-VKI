import re
import sqlite3
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from src.database import DatabaseRepository


class ForumParser:
    """
    Класс для извлечения информации (парсинга) со страниц форумов и структурированных веб-ресурсов.
    """

    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    def __init__(self, user_agent: Optional[str] = None, timeout: int = 10):
        """
        Инициализация парсера.

        :param user_agent: Пользовательский User-Agent для сетевых запросов.
        :param timeout: Таймаут для сетевых запросов в секундах.
        """
        self.headers = {
            "User-Agent": user_agent or self.DEFAULT_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        self.timeout = timeout

    def fetch_page(self, url: str) -> str:
        """
        Выполняет HTTP-запрос к указанному URL с передачей заголовков и возвращает HTML-код.

        :param url: URL-адрес страницы.
        :return: HTML-содержимое страницы.
        :raises requests.HTTPError: При ошибке HTTP-статуса (4xx, 5xx).
        :raises requests.RequestException: При общих сетевых ошибках.
        """
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        return response.text

    def parse_html(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Разбирает HTML-код и извлекает список комментариев/сообщений.

        Поддерживает стандартную разметку форумов:
        - Контейнеры постов: элементы с классами 'comment', 'post', 'forum-post', 'message-item'.
        - ID: из атрибутов data-id, data-comment-id, id или ссылки.
        - Автор: элементы с классами 'author', 'author-name', 'username', 'user-nickname'.
        - Текст: элементы с классами 'comment-text', 'post-message', 'message-body', 'post-content'.

        :param html_content: Исходный HTML-код страницы.
        :return: Список словарей вида [{'id': int, 'name': str, 'message': str}, ...]
        """
        if not html_content or not html_content.strip():
            return []

        try:
            soup = BeautifulSoup(html_content, "lxml")
        except Exception:
            soup = BeautifulSoup(html_content, "html.parser")
        results: List[Dict[str, Any]] = []

        # Селекторы для поиска блоков сообщений
        post_elements = soup.select(
            ".comment, .post, .forum-post, .message-item, [data-comment-id], [data-id]"
        )

        for element in post_elements:
            # 1. Извлечение ID
            comment_id = self._extract_id(element)
            if comment_id is None:
                continue

            # 2. Извлечение логина автора
            author_name = self._extract_author(element)
            if not author_name:
                continue

            # 3. Извлечение текста сообщения (с сохранением внутренней HTML-разметки или в виде текста)
            message_text = self._extract_message(element)
            if not message_text:
                continue

            results.append({
                "id": comment_id,
                "name": author_name,
                "message": message_text
            })

        return results

    def _extract_id(self, element) -> Optional[int]:
        """Вспомогательный метод для извлечения целочисленного ID поста."""
        # 1. Проверяем атрибуты данных data-id и data-comment-id
        for attr in ("data-id", "data-comment-id"):
            val = element.get(attr)
            if val and str(val).isdigit():
                return int(val)

        # 2. Проверяем атрибут id (например, 'post-105' или 'comment_42')
        elem_id = element.get("id")
        if elem_id:
            # Ищем последовательность цифр
            digits = re.findall(r"\d+", str(elem_id))
            if digits:
                return int(digits[0])

        # 3. Проверяем наличие дочерних ссылок или элементов с ID
        id_node = element.select_one(".comment-id, .post-id, a[data-id]")
        if id_node:
            val = id_node.get("data-id") or id_node.get_text(strip=True)
            digits = re.findall(r"\d+", str(val))
            if digits:
                return int(digits[0])

        return None

    def _extract_author(self, element) -> Optional[str]:
        """Вспомогательный метод для извлечения имени автора."""
        author_node = element.select_one(
            ".author, .author-name, .username, .user-nickname, .user-name, [itemprop='author']"
        )
        if author_node:
            name = author_node.get_text(strip=True)
            if name:
                return name[:DatabaseRepository.MAX_NAME_LENGTH]
        return None

    def _extract_message(self, element) -> Optional[str]:
        """Вспомогательный метод для извлечения содержимого сообщения."""
        message_node = element.select_one(
            ".comment-text, .post-message, .message-body, .post-content, .text"
        )
        if message_node:
            # Извлекаем внутреннее HTML-содержимое поста
            inner_html = "".join(str(child) for child in message_node.children).strip()
            if not inner_html:
                inner_html = message_node.get_text(strip=True)

            if inner_html:
                return inner_html[:DatabaseRepository.MAX_MESSAGE_LENGTH]
        return None

    def parse_page(self, url: str) -> List[Dict[str, Any]]:
        """
        Загружает страницу по URL и извлекает все найденные комментарии.

        :param url: URL-адрес темы форума.
        :return: Список извлеченных комментариев.
        """
        html = self.fetch_page(url)
        return self.parse_html(html)

    def save_to_db(
        self,
        parsed_data: List[Dict[str, Any]],
        repository: DatabaseRepository,
        ignore_duplicates: bool = True
    ) -> int:
        """
        Сохраняет спарсенные данные в базу данных через репозиторий.

        :param parsed_data: Список словарей с комментариями.
        :param repository: Экземпляр DatabaseRepository.
        :param ignore_duplicates: Пропускать дубликаты ID (True) или выбрасывать ошибку (False).
        :return: Количество успешно сохраненных комментариев.
        """
        saved_count = 0
        for item in parsed_data:
            try:
                repository.add(
                    comment_id=item["id"],
                    username=item["name"],
                    message=item["message"]
                )
                saved_count += 1
            except sqlite3.IntegrityError:
                if not ignore_duplicates:
                    raise
                # При ignore_duplicates=True пропускаем уже существующие записи
                continue
        return saved_count
