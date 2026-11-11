import re
import sqlite3
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from src.database import DatabaseRepository


class ForumParser:
    """
    Парсер комментариев, оптимизированный под разметку 4PDA.
    """

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    def __init__(self, timeout: int = 10):
        self.headers = {"User-Agent": self.USER_AGENT}
        self.timeout = timeout

    def fetch_page(self, url: str) -> str:
        """
        1. Отправка HTTP GET-запроса через библиотеку requests
        с подменой User-Agent и правильным декодированием windows-1251.
        """
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        
        # 4PDA использует кодировку windows-1251
        if response.encoding and response.encoding.lower() in ("iso-8859-1", "utf-8"):
            response.encoding = response.apparent_encoding or "windows-1251"
            
        return response.text

    def parse_html(self, html_content: str) -> List[Dict[str, Any]]:
        """
        2. Поиск и извлечение комментариев из HTML через BeautifulSoup.
        """
        if not html_content or not html_content.strip():
            return []

        soup = BeautifulSoup(html_content, "html.parser")
        results: List[Dict[str, Any]] = []

        # На 4PDA каждый блок комментария имеет атрибут id="comment-XXXXXX"
        comment_blocks = soup.find_all(
            lambda tag: tag.name == "div" and tag.has_attr("id") and re.match(r"^comment-\d+$", tag["id"])
        )

        for block in comment_blocks:
            # Извлекаем ID (число из 'comment-10819774')
            digits = re.findall(r"\d+", block["id"])
            if not digits:
                continue
            comment_id = int(digits[0])

            # Извлекаем логин автора (<span class="nickname">...</span>)
            nickname_elem = block.select_one(".nickname")
            if not nickname_elem:
                continue
            username = nickname_elem.get_text(strip=True)[:DatabaseRepository.MAX_NAME_LENGTH]

            # Извлекаем текст комментария (<div class="content">...</div>)
            content_elem = block.select_one(".content")
            if not content_elem:
                continue

            # Сохраняем текст сообщения (включая HTML-разметку, например <br/>)
            message_html = "".join(str(child) for child in content_elem.children).strip()
            if not message_html:
                message_html = content_elem.get_text(strip=True)

            message_html = message_html[:DatabaseRepository.MAX_MESSAGE_LENGTH]

            results.append({
                "id": comment_id,
                "name": username,
                "message": message_html
            })

        return results

    def parse_page(self, url: str) -> List[Dict[str, Any]]:
        """
        Связующий метод: скачивает HTML по ссылке и парсит комментарии.
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
        3. Сохранение полученных комментариев в базу данных SQLite.
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
                continue
        return saved_count
