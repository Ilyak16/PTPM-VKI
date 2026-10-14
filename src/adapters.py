import logging

from interfaces import ExternalDependency, UserInteraction


class ConsoleUserInteraction(UserInteraction):
    def get_input(self):
        return (
            input("Введите длину стороны A: "),
            input("Введите длину стороны B: "),
            input("Введите длину стороны C: "),
        )


class SimulatedExternalDependency(ExternalDependency):
    """Локальная заглушка сторонней службы; сетевые запросы не выполняются."""

    def __init__(self):
        self.sent_messages = []

    def send(self, message):
        self.sent_messages.append(message)
        logging.info("Имитация передачи результата: %s", message)
        return True
