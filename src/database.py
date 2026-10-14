import json
import sqlite3


class TriangleDatabase:
    """SQLite-хранилище результатов расчёта треугольников."""

    def __init__(self, database_path=":memory:"):
        self.connection = sqlite3.connect(database_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS triangles (
                length1 TEXT NOT NULL,
                length2 TEXT NOT NULL,
                length3 TEXT NOT NULL,
                triangle_type TEXT NOT NULL,
                error_message TEXT,
                vertices TEXT,
                PRIMARY KEY (length1, length2, length3)
            )
            """
        )
        self.connection.commit()

    def add_data(
        self,
        length1,
        length2,
        length3,
        triangle_type,
        error_message=None,
        vertices=None,
    ):
        """Добавляет или обновляет результат для заданных сторон."""
        serialized_vertices = json.dumps(vertices) if vertices is not None else None
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO triangles
                    (length1, length2, length3, triangle_type, error_message, vertices)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(length1, length2, length3) DO UPDATE SET
                    triangle_type = excluded.triangle_type,
                    error_message = excluded.error_message,
                    vertices = excluded.vertices
                """,
                (
                    str(length1),
                    str(length2),
                    str(length3),
                    triangle_type,
                    error_message,
                    serialized_vertices,
                ),
            )

    def get_data(self, length1, length2, length3):
        """Возвращает сохранённую запись или None, если её нет."""
        row = self.connection.execute(
            """
            SELECT length1, length2, length3, triangle_type, error_message, vertices
            FROM triangles
            WHERE length1 = ? AND length2 = ? AND length3 = ?
            """,
            (str(length1), str(length2), str(length3)),
        ).fetchone()
        if row is None:
            return None

        result = dict(row)
        result["vertices"] = (
            [tuple(point) for point in json.loads(result["vertices"])]
            if result["vertices"] is not None
            else None
        )
        return result

    def delete_data(self, length1, length2, length3):
        """Удаляет запись; возвращает True, если запись существовала."""
        with self.connection:
            cursor = self.connection.execute(
                """
                DELETE FROM triangles
                WHERE length1 = ? AND length2 = ? AND length3 = ?
                """,
                (str(length1), str(length2), str(length3)),
            )
        return cursor.rowcount > 0

    def close(self):
        self.connection.close()
