from abc import ABC, abstractmethod


class UserInteraction(ABC):
    """Интерфейс получения исходных данных от пользователя."""

    @abstractmethod
    def get_input(self):
        """Возвращает три длины сторон треугольника."""


class ExternalDependency(ABC):
    """Интерфейс сторонней зависимости для передачи результата."""

    @abstractmethod
    def send(self, message):
        """Имитирует отправку сообщения и возвращает результат операции."""
