import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from Delivery import calculate_delivery_cost

class TestDeliveryService(unittest.TestCase):

    def test_base_usual_delivery(self):
        """Базовый расчет: вес 2кг, дистанция 100км, обычный"""
        # base=200, dist=500, total=700
        cost, date = calculate_delivery_cost(2.0, 100, "обычный")
        self.assertEqual(cost, 700)

    def test_express_delivery_cost(self):
        """Экспресс-доставка должна стоить ДОРОЖЕ, а не дешевле"""
        cost, date = calculate_delivery_cost(2.0, 100, "обычный", is_express=True)
        self.assertGreater(cost, 700)  # Упадет на оригинальном коде (там *= 0.5)

    def test_weight_limit_min(self):
        """Проверка нижнего лимита веса"""
        cost, date = calculate_delivery_cost(0.05, 100, "обычный")
        self.assertEqual(cost, -1)

    def test_weight_limit_max(self):
        """Проверка верхнего лимита веса"""
        cost, date = calculate_delivery_cost(51.0, 100, "обычный")
        self.assertEqual(cost, -1)

    def test_distance_limit_min(self):
        """Проверка нижнего лимита дистанции"""
        cost, date = calculate_delivery_cost(2.0, 0, "обычный")
        self.assertEqual(cost, -1)

    def test_distance_limit_max(self):
        """Проверка верхнего лимита дистанции"""
        cost, date = calculate_delivery_cost(2.0, 5001, "обычный")
        self.assertEqual(cost, -1)

    def test_invalid_package_type(self):
        """Проверка несуществующего типа посылки"""
        cost, date = calculate_delivery_cost(2.0, 100, "газовый")
        self.assertEqual(cost, -1)

    def test_fragile_package_cost(self):
        """Проверка наценки за хрупкость"""
        cost, date = calculate_delivery_cost(2.0, 100, "хрупкий")
        self.assertEqual(cost, 1000)  # 700 + 300

    def test_dangerous_package_cost(self):
        """Проверка наценки за опасность"""
        cost, date = calculate_delivery_cost(2.0, 100, "опасный")
        self.assertEqual(cost, 1700)  # 700 + 1000

    def test_weight_coefficient_medium(self):
        """Проверка коэффициента для среднего веса (5 < w < 20)"""
        cost, date = calculate_delivery_cost(10.0, 100, "обычный")
        self.assertEqual(cost, 840)  # 700 * 1.2

    def test_weight_coefficient_heavy(self):
        """Проверка коэффициента для тяжелого веса (w >= 20)"""
        cost, date = calculate_delivery_cost(25.0, 100, "обычный")
        self.assertEqual(cost, 1050)  # 700 * 1.5

    def test_express_days_minimum(self):
        """Экспресс-доставка не должна доставлять за 0 дней"""
        # Дистанция 100 км -> базово 1 день. Экспресс // 2 = 0 дней. Баг!
        cost, date = calculate_delivery_cost(2.0, 100, "обычный", is_express=True)
        self.assertEqual(date, "2026-09-04")  # Дата отправки + минимум 1 день

if __name__ == '__main__':
    unittest.main()