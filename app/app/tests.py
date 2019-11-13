from django.test import TestCase

from app.calc import add


class ClacTests(TestCase):
    def test_add_numbers(self):
        """test that  it works"""
        self.assertEqual(add(3, 8), 11, "not added correctly")
