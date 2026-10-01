import logging
import math
import os
import sys


def setup_logging():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(base_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    log_format = "%(asctime)s | [%(levelname)-7s] | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=logging.DEBUG,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(os.path.join(logs_dir, "file_txt.log"), encoding="utf-8"),
        ],
    )


def calculate_vertices(a, b, c):
    ax, ay = 0.0, 0.0
    bx, by = c, 0.0

    cx = (b * b + c * c - a * a) / (2 * c)
    cy_squared = b * b - cx * cx
    cy = math.sqrt(cy_squared) if cy_squared > 0 else 0.0

    raw_points = [(ax, ay), (bx, by), (cx, cy)]
    logging.debug(f"Сырые координаты вершин: {raw_points}")

    xs = [p[0] for p in raw_points]
    ys = [p[1] for p in raw_points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    width = max_x - min_x
    height = max_y - min_y
    max_side = max(width, height)

    scale = (100.0 / max_side) if max_side > 0 else 1.0

    scaled_points = [
        (round((x - min_x) * scale), round((y - min_y) * scale))
        for (x, y) in raw_points
    ]

    shift_x, shift_y = scaled_points[0]
    result = [(int(x - shift_x), int(y - shift_y)) for (x, y) in scaled_points]

    logging.debug(f"Координаты после масштабирования и сдвига: {result}")
    return result


def calculate_triangle(str_a, str_b, str_c):
    logging.info(f"Запрос на расчёт треугольника: A='{str_a}', B='{str_b}', C='{str_c}'")

    try:
        a = float(str_a)
        b = float(str_b)
        c = float(str_c)
    except (ValueError, TypeError) as ex:
        logging.error("Некорректные (нечисловые) входные данные.")
        logging.exception("Заход в блок обработки исключения:")
        return "", [(-2, -2), (-2, -2), (-2, -2)]

    logging.debug(f"Входные данные приведены к float: a={a}, b={b}, c={c}")

    if a <= 0 or b <= 0 or c <= 0:
        logging.warning("Одна или несколько сторон не являются положительными числами.")
        return "не треугольник", [(-1, -1), (-1, -1), (-1, -1)]

    if (a + b <= c) or (a + c <= b) or (b + c <= a):
        logging.warning(f"Стороны a={a}, b={b}, c={c} не образуют треугольник.")
        return "не треугольник", [(-1, -1), (-1, -1), (-1, -1)]

    if a == b == c:
        triangle_type = "равносторонний"
    elif a == b or b == c or a == c:
        triangle_type = "равнобедренный"
    else:
        triangle_type = "разносторонний"

    logging.info(f"Определён тип треугольника: {triangle_type}")

    vertices = calculate_vertices(a, b, c)

    logging.info(f"Успешный запрос. Тип: '{triangle_type}', координаты: {vertices}")
    return triangle_type, vertices


def main():
    setup_logging()
    logging.info("Логгер успешно сконфигурирован")
    logging.info("Приложение запущено")

    try:
        str_a = input("Введите длину стороны A: ")
        str_b = input("Введите длину стороны B: ")
        str_c = input("Введите длину стороны C: ")

        triangle_type, vertices = calculate_triangle(str_a, str_b, str_c)

        print("\n--- Результат ---")
        print(f"Тип треугольника: '{triangle_type}'")
        print(f"Координаты вершин: {vertices}")

    except Exception as ex:
        logging.critical("Непредвиденная ошибка в работе приложения.")
        logging.exception("Трассировка стека:")
    finally:
        logging.info("Приложение завершило работу")


if __name__ == "__main__":
    main()