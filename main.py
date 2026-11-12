from src.database import DatabaseRepository
from src.parser import ForumParser


TARGET_URL = (
    "https://4pda.to/2026/10/29/462736/"
    "globalnaya_coloros_17_vyshla_dlya_oneplus_oppo_i_realme_chto_vy_poluchite/"
)


def main():
    print("=" * 70)
    print("Парсер 4PDA и репозиторий SQLite")
    print("=" * 70)

    import os
    db_file = "comments_4pda.db"
    if os.path.exists(db_file):
        os.remove(db_file)

    print(f"\n[1] Создание базы данных SQLite: '{db_file}'...")
    repo = DatabaseRepository(db_file)


    print(f"\n[2] Загрузка и парсинг страницы по URL:\n    {TARGET_URL}")
    parser = ForumParser()
    comments = parser.parse_page(TARGET_URL)
    print(f"    -> Успешно извлечено комментариев: {len(comments)}")

    if not comments:
        print("Комментарии не найдены.")
        repo.close()
        return
    print("\n[Примеры первых 3 извлеченных комментариев]:")
    for item in comments[:3]:
        snippet = item["message"].replace("\n", " ")[:90]
        print(f" - [ID {item['id']}] Автор: '{item['name']}' | Сообщение: {snippet}...")

    print("\n[3] Сохранение комментариев в таблицу 'comments'...")
    saved_count = parser.save_to_db(comments, repo, ignore_duplicates=True)
    print(f"    -> Новых записей успешно добавлено в БД: {saved_count}")

    print("\n[4] Проверка методов репозитория DatabaseRepository:")
    
    first_id = comments[0]["id"]
    record = repo.get_by_id(first_id)
    print(f"    * get_by_id({first_id}):")
    print(f"      Имя: {record['name']}")
    print(f"      Текст: {record['message'][:100]}...")

    first_author = comments[0]["name"]
    author_comments = repo.get_by_name(first_author)
    print(f"\n    * get_by_name('{first_author}'): найдено {len(author_comments)} сообщений")
    for c in author_comments[:3]:
        print(f"      - ID {c['id']}: {c['message'][:80]}...")

    print(f"\n    * update({first_id}, <новое сообщение>):")
    new_text = "<b>[Отредактировано модератором]</b> Данное сообщение прошло проверку."
    repo.update(first_id, new_text)
    updated = repo.get_by_id(first_id)
    print(f"      Обновленный текст в БД: {updated['message']}")

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
