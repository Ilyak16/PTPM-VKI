import unittest
import sys
import os

# Добавляем путь к src, если структура папок соответствует рекомендациям из README
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from main import calculate_triangle

class TestTriangleCalculator(unittest.TestCase):

    def test_equilateral_triangle(self):
        """Проверка равностороннего треугольника"""
        t_type, vertices = calculate_triangle("3", "3", "3")
        self.assertEqual(t_type, "равносторонний")
        self.assertEqual(len(vertices), 3)

    def test_isosceles_triangle(self):
        """Проверка равнобедренного треугольника"""
        t_type, _ = calculate_triangle("3", "3", "4")
        self.assertEqual(t_type, "равнобедренный")

    def test_scalene_triangle(self):
        """Проверка разностороннего треугольника"""
        t_type, _ = calculate_triangle("3", "4", "5")
        self.assertEqual(t_type, "разносторонний")

    def test_invalid_triangle_sum(self):
        """Проверка неравенства треугольника (сумма двух сторон равна третьей)"""
        t_type, vertices = calculate_triangle("1", "2", "3")
        self.assertEqual(t_type, "не треугольник")
        self.assertEqual(vertices, [(-1, -1), (-1, -1), (-1, -1)])

    def test_negative_side(self):
        """Проверка на отрицательные значения сторон"""
        t_type, vertices = calculate_triangle("-1", "2", "3")
        self.assertEqual(t_type, "не треугольник")

    def test_zero_side(self):
        """Проверка на нулевые значения сторон"""
        t_type, vertices = calculate_triangle("0", "2", "3")
        self.assertEqual(t_type, "не треугольник")

    def test_non_numeric_input(self):
        """Проверка обработки нечисловых данных (строки)"""
        t_type, vertices = calculate_triangle("abc", "2", "3")
        self.assertEqual(t_type, "")
        self.assertEqual(vertices, [(-2, -2), (-2, -2), (-2, -2)])

    def test_float_sides(self):
        """Проверка работы с дробными значениями сторон"""
        t_type, _ = calculate_triangle("3.5", "4.5", "5.5")
        self.assertEqual(t_type, "разносторонний")

    def test_large_numbers(self):
        """Проверка работы с очень большими числами"""
        t_type, _ = calculate_triangle("1000", "1000", "1000")
        self.assertEqual(t_type, "равносторонний")

    def test_empty_string_input(self):
        """Проверка обработки пустой строки"""
        t_type, vertices = calculate_triangle("", "2", "3")
        self.assertEqual(t_type, "")
        self.assertEqual(vertices, [(-2, -2), (-2, -2), (-2, -2)])

if __name__ == '__main__':
    unittest.main()