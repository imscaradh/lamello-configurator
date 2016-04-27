from django.test import TestCase
from .services import calc_bisec
import math


class ServicesTestCase(TestCase):

    def setUp(self):
        # nothing here
        return

    def test_calc_bisec(self):
        m1 = 20
        m2 = 17
        angle = 90

        result = calc_bisec(m1, m2, angle)
        is_close = math.isclose(result, 7.88, rel_tol=1e-3)
        self.assertTrue(is_close)
