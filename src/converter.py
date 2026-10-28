import math

class Converter:
    @staticmethod
    def do(x: float) -> int:
        if not isinstance(x, (int, float)):
            raise TypeError(f"Ожидалось число типа float или int, получено: {type(x).__name__}")
        if math.isnan(x):
            raise ValueError("Значение x не может быть NaN")
        if not math.isinf(x):
            x = round(float(x), 1)
        if x >= 100.7:
            return 1000
        elif x > 0.0:
            return int(x)
        elif x == 0.0:
            raise ValueError("Значение x не должно быть равно 0.0")
        elif x >= -30.4:
            return int(x) - 5
        else:
            return -2000
