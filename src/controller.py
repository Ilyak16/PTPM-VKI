from adapters import ConsoleUserInteraction, SimulatedExternalDependency
from database import TriangleDatabase
from main import TriangleCalculator


class Controller:
    """Координирует ввод, вычисление, кэширование и отправку результата."""

    def __init__(
        self,
        user_interaction=None,
        database=None,
        external_dependency=None,
        calculator=None,
    ):
        self.user_interaction = user_interaction or ConsoleUserInteraction()
        self.database = database or TriangleDatabase()
        self.external_dependency = external_dependency or SimulatedExternalDependency()
        self.calculator = calculator or TriangleCalculator()

    def run(self):
        sides = tuple(str(side) for side in self.user_interaction.get_input())
        if len(sides) != 3:
            raise ValueError("Необходимо передать ровно три длины сторон.")

        record = self.database.get_data(*sides)
        from_cache = record is not None

        if from_cache:
            triangle_type = record["triangle_type"]
            error_message = record["error_message"]
            vertices = record["vertices"]
        else:
            triangle_type, vertices = self.calculator.calculate_triangle(*sides)
            if triangle_type == "":
                error_message = "Некорректные (нечисловые) входные данные."
            elif triangle_type == "не треугольник":
                error_message = "Заданные длины сторон не образуют треугольник."
            else:
                error_message = None

            self.database.add_data(
                *sides,
                triangle_type=triangle_type,
                error_message=error_message,
                vertices=vertices,
            )

        result = {
            "sides": sides,
            "triangle_type": triangle_type,
            "vertices": vertices,
            "error_message": error_message,
            "from_cache": from_cache,
        }
        self.external_dependency.send(self._format_result(result))
        return result

    @staticmethod
    def _format_result(result):
        message = (
            f"Тип треугольника: {result['triangle_type'] or 'не определён'}; "
            f"координаты вершин: {result['vertices']}"
        )
        if result["error_message"]:
            message += f"; ошибка: {result['error_message']}"
        return message
