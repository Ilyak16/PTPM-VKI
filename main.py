"""
Демонстрация работы парсера на реальной странице 4PDA и сохранение данных в SQLite.
"""
from src.database import DatabaseRepository
from src.parser import ForumParser


TARGET_URL = (
    "https://4pda.to/2026/10/29/462736/"
    "globalnaya_coloros_17_vyshla_dlya_oneplus_oppo_i_realme_chto_vy_poluchite/"
)


def main():
    print("=" * 70)
    print("Парсер 4PDA и репозиторий SQLite (Лабораторная работа)")
    print("=" * 70)

    # 1. Инициализация базы данных (удаляем старый файл для наглядной демонстрации)
    import os
    db_file = "comments_4pda.db"
    if os.path.exists(db_file):
        os.remove(db_file)

    print(f"\n[1] Создание базы данных SQLite: '{db_file}'...")
    repo = DatabaseRepository(db_file)

    # 2. Инициализация парсера и загрузка страницы
    print(f"\n[2] Загрузка и парсинг страницы по URL:\n    {TARGET_URL}")
    parser = ForumParser()
    comments = parser.parse_page(TARGET_URL)
    print(f"    -> Успешно извлечено комментариев: {len(comments)}")

    if not comments:
        print("Комментарии не найдены.")
        repo.close()
        return

    # Вывод первых 3 комментариев для наглядности
    print("\n[Примеры первых 3 извлеченных комментариев]:")
    for item in comments[:3]:
        snippet = item["message"].replace("\n", " ")[:90]
        print(f" - [ID {item['id']}] Автор: '{item['name']}' | Сообщение: {snippet}...")

    # 3. Сохранение данных в базу данных SQLite
    print("\n[3] Сохранение комментариев в таблицу 'comments'...")
    saved_count = parser.save_to_db(comments, repo, ignore_duplicates=True)
    print(f"    -> Новых записей успешно добавлено в БД: {saved_count}")

    # 4. Проверка работы методов выборки из БД
    print("\n[4] Проверка методов репозитория DatabaseRepository:")
    
    # 4.1. get_by_id
    first_id = comments[2]["id"]
    record = repo.get_by_id(first_id)
    print(f"    * get_by_id({first_id}):")
    print(f"      Имя: {record['name']}")
    print(f"      Текст: {record['message'][:100]}...")

    # 4.2. get_by_name (ищем сообщения первого автора)
    first_author = comments[2]["name"]
    author_comments = repo.get_by_name(first_author)
    print(f"\n    * get_by_name('{first_author}'): найдено {len(author_comments)} сообщений")
    for c in author_comments[:3]:
        print(f"      - ID {c['id']}: {c['message'][:80]}...")

    # 4.3. update (редактирование сообщения)
    print(f"\n    * update({first_id}, <новое сообщение>):")
    new_text = "<b>[Отредактировано модератором]</b> Данное сообщение прошло проверку."
    repo.update(first_id, new_text)
    updated = repo.get_by_id(first_id)
    print(f"      Обновленный текст в БД: {updated['message']}")

    # 4.4. delete (удаление записи)
    last_id = comments[-1]["id"]
    print(f"\n    * delete({last_id}):")
    deleted = repo.delete(last_id)
    print(f"      Результат удаления: {deleted}")
    print(f"      Проверка наличия в БД: {repo.get_by_id(last_id)}")

    repo.close()
    print("\n" + "=" * 70)
    print("Демонстрация завершена успешно!")
    print("=" * 70)


if __name__ == "__main__":
    main()
