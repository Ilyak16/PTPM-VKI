import os
import sys
import unittest

# Добавляем путь к src в sys.path для корректного импорта при любых способах запуска тестов
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from converter import Converter


class TestConverter(unittest.TestCase):
    """
    Набор модульных тестов для класса Converter и метода do(x: float) -> int.
    Проверяет все диапазоны, граничные значения, исключения и типы данных.
    """

    # -------------------------------------------------------------------------
    # Диапазон 1: x ∈ [100.7; + ∞) -> возвращает 1000
    # -------------------------------------------------------------------------

    def test_upper_range_exact_boundary(self):
        """Граничное значение: левая граница диапазона [100.7; +∞) -> 1000"""
        self.assertEqual(Converter.do(100.7), 1000)

    def test_upper_range_just_above_boundary(self):
        """Значение чуть выше границы диапазона [100.7; +∞) -> 1000"""
        self.assertEqual(Converter.do(100.8), 1000)

    def test_upper_range_typical_value(self):
        """Типичное положительное значение внутри [100.7; +∞) -> 1000"""
        self.assertEqual(Converter.do(250.5), 1000)

    def test_upper_range_large_value(self):
        """Большое положительное значение -> 1000"""
        self.assertEqual(Converter.do(99999.9), 1000)

    def test_upper_range_infinity(self):
        """Положительная бесконечность (+inf) -> 1000"""
        self.assertEqual(Converter.do(float("inf")), 1000)

    # -------------------------------------------------------------------------
    # Диапазон 2: x ∈ (0; 100.7) -> возвращает int(x) (отбрасывание дробной части)
    # -------------------------------------------------------------------------

    def test_positive_range_upper_boundary(self):
        """Граничное значение: непосредственно перед 100.7 с шагом 0.1 (100.6) -> 100"""
        self.assertEqual(Converter.do(100.6), 100)

    def test_positive_range_typical_examples(self):
        """Типичные значения из диапазона (0; 100.7) -> int(x)"""
        self.assertEqual(Converter.do(65.7), 65)
        self.assertEqual(Converter.do(50.0), 50)
        self.assertEqual(Converter.do(15.9), 15)
        self.assertEqual(Converter.do(1.0), 1)

    def test_positive_range_less_than_one(self):
        """Значения меньше 1, но больше 0 -> 0"""
        self.assertEqual(Converter.do(0.9), 0)
        self.assertEqual(Converter.do(0.5), 0)

    def test_positive_range_lower_boundary(self):
        """Граничное значение: минимальное положительное число с шагом 0.1 (0.1) -> 0"""
        self.assertEqual(Converter.do(0.1), 0)

    # -------------------------------------------------------------------------
    # Точка: x == 0.0 -> генерируется ValueError
    # -------------------------------------------------------------------------

    def test_zero_raises_value_error(self):
        """Проверка генерации ValueError при x == 0.0"""
        with self.assertRaises(ValueError):
            Converter.do(0.0)

    def test_negative_zero_raises_value_error(self):
        """Проверка генерации ValueError при x == -0.0"""
        with self.assertRaises(ValueError):
            Converter.do(-0.0)

    def test_integer_zero_raises_value_error(self):
        """Проверка генерации ValueError при x == 0 (int)"""
        with self.assertRaises(ValueError):
            Converter.do(0)

    # -------------------------------------------------------------------------
    # Диапазон 3: x ∈ [-30.4; 0) -> возвращает int(x) - 5
    # -------------------------------------------------------------------------

    def test_negative_range_upper_boundary(self):
        """Граничное значение: максимальное отрицательное число с шагом 0.1 (-0.1) -> int(-0.1) - 5 = -5"""
        self.assertEqual(Converter.do(-0.1), -5)

    def test_negative_range_less_than_minus_one(self):
        """Значения в диапазоне (-1; 0) -> int(x) - 5 = 0 - 5 = -5"""
        self.assertEqual(Converter.do(-0.5), -5)
        self.assertEqual(Converter.do(-0.9), -5)

    def test_negative_range_typical_examples(self):
        """Типичные значения из диапазона [-30.4; 0) -> int(x) - 5"""
        # int(-1.0) - 5 = -1 - 5 = -6
        self.assertEqual(Converter.do(-1.0), -6)
        # int(-10.5) - 5 = -10 - 5 = -15
        self.assertEqual(Converter.do(-10.5), -15)
        # int(-25.8) - 5 = -25 - 5 = -30
        self.assertEqual(Converter.do(-25.8), -30)

    def test_negative_range_just_above_lower_boundary(self):
        """Значение чуть выше левой границы (-30.3) -> int(-30.3) - 5 = -35"""
        self.assertEqual(Converter.do(-30.3), -35)

    def test_negative_range_exact_lower_boundary(self):
        """Граничное значение: левая граница диапазона [-30.4; 0) (-30.4) -> int(-30.4) - 5 = -35"""
        self.assertEqual(Converter.do(-30.4), -35)

    # -------------------------------------------------------------------------
    # Диапазон 4: x ∈ (-∞ ; -30.5] -> возвращает -2000
    # -------------------------------------------------------------------------

    def test_far_negative_exact_upper_boundary(self):
        """Граничное значение: правая граница диапазона (-∞; -30.5] (-30.5) -> -2000"""
        self.assertEqual(Converter.do(-30.5), -2000)

    def test_far_negative_just_below_boundary(self):
        """Значение чуть ниже границы (-30.6) -> -2000"""
        self.assertEqual(Converter.do(-30.6), -2000)

    def test_far_negative_readme_example(self):
        """Значение из примера в README.md (-94.5) -> -2000"""
        self.assertEqual(Converter.do(-94.5), -2000)

    def test_far_negative_large_value(self):
        """Большое по модулю отрицательное значение (-10000.0) -> -2000"""
        self.assertEqual(Converter.do(-10000.0), -2000)

    def test_far_negative_minus_infinity(self):
        """Отрицательная бесконечность (-inf) -> -2000"""
        self.assertEqual(Converter.do(float("-inf")), -2000)

    # -------------------------------------------------------------------------
    # Дополнительные проверки: типы данных, NaN и особенности вызова метода
    # -------------------------------------------------------------------------

    def test_result_type_is_always_int(self):
        """Проверка, что возвращаемое значение всегда имеет тип int"""
        sample_inputs = [150.0, 100.7, 100.6, 50.5, 0.1, -0.1, -15.2, -30.4, -30.5, -100.0]
        for x in sample_inputs:
            res = Converter.do(x)
            self.assertIsInstance(res, int, f"Результат для x={x} должен быть int, получен {type(res)}")

    def test_nan_raises_value_error(self):
        """Передача NaN вызывает ValueError"""
        with self.assertRaises(ValueError):
            Converter.do(float("nan"))

    def test_invalid_types_raise_type_error(self):
        """Передача аргументов нечислового типа должна вызывать TypeError"""
        invalid_inputs = ["10.5", None, [10.5], {"x": 10.5}, (1.0,)]
        for invalid in invalid_inputs:
            with self.subTest(invalid=invalid):
                with self.assertRaises(TypeError):
                    Converter.do(invalid)

    def test_can_be_called_on_instance(self):
        """Статический метод do должен успешно вызываться и через экземпляр класса"""
        converter_instance = Converter()
        self.assertEqual(converter_instance.do(100.7), 1000)
        self.assertEqual(converter_instance.do(50.5), 50)
        self.assertEqual(converter_instance.do(-30.5), -2000)


if __name__ == "__main__":
    unittest.main()
