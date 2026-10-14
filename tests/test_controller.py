import os
import sys
import unittest
from unittest.mock import Mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from controller import Controller
from database import TriangleDatabase
from main import TriangleCalculator


class TestTriangleControllerIntegration(unittest.TestCase):
    def setUp(self):
        self.database = TriangleDatabase(":memory:")
        self.user_interaction = Mock()
        self.external_dependency = Mock()
        self.controller = Controller(
            user_interaction=self.user_interaction,
            database=self.database,
            external_dependency=self.external_dependency,
            calculator=TriangleCalculator(),
        )

    def tearDown(self):
        self.database.close()

    def test_new_triangle_is_calculated_saved_and_sent(self):
        self.user_interaction.get_input.return_value = ("3", "4", "5")

        result = self.controller.run()

        self.assertEqual(result["triangle_type"], "разносторонний")
        self.assertFalse(result["from_cache"])
        self.assertIsNone(result["error_message"])
        saved = self.database.get_data("3", "4", "5")
        self.assertEqual(saved["triangle_type"], "разносторонний")
        self.assertEqual(saved["vertices"], result["vertices"])
        self.external_dependency.send.assert_called_once()
        self.assertIn("разносторонний", self.external_dependency.send.call_args.args[0])

    def test_existing_triangle_is_loaded_without_recalculation(self):
        self.user_interaction.get_input.return_value = ("3", "3", "3")
        first_result = self.controller.run()
        self.controller.calculator.calculate_triangle = Mock(
            side_effect=AssertionError("Расчёт не должен повторяться для записи из БД")
        )

        cached_result = self.controller.run()

        self.assertEqual(cached_result["triangle_type"], first_result["triangle_type"])
        self.assertEqual(cached_result["vertices"], first_result["vertices"])
        self.assertTrue(cached_result["from_cache"])
        self.controller.calculator.calculate_triangle.assert_not_called()
        self.assertEqual(self.external_dependency.send.call_count, 2)

    def test_invalid_triangle_error_is_saved_and_returned_from_cache(self):
        self.user_interaction.get_input.return_value = ("1", "2", "3")

        first_result = self.controller.run()
        self.controller.calculator.calculate_triangle = Mock(
            side_effect=AssertionError("Ошибка должна быть загружена из БД")
        )
        cached_result = self.controller.run()

        self.assertEqual(first_result["triangle_type"], "не треугольник")
        self.assertIsNotNone(first_result["error_message"])
        self.assertEqual(cached_result["error_message"], first_result["error_message"])
        self.assertTrue(cached_result["from_cache"])


class TestTriangleDatabase(unittest.TestCase):
    def test_add_get_and_delete_record(self):
        database = TriangleDatabase(":memory:")
        try:
            database.add_data("5", "5", "5", "равносторонний", vertices=[(0, 0)])

            self.assertEqual(
                database.get_data("5", "5", "5")["triangle_type"], "равносторонний"
            )
            self.assertTrue(database.delete_data("5", "5", "5"))
            self.assertIsNone(database.get_data("5", "5", "5"))
            self.assertFalse(database.delete_data("5", "5", "5"))
        finally:
            database.close()


if __name__ == "__main__":
    unittest.main()
