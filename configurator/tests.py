from django.test import TestCase
from .services import BisecService
import math


class ServicesTestCase(TestCase):

    def setUp(self):
        # nothing here
        return

    def test_calc_bisec(self):
        m1 = 20
        m2 = 17
        angle = 90

        bisec = BisecService(m1, m2, angle)
        result = bisec.check()
        print(result)
        is_close = math.isclose(result['cnc']['position'], 7.87, rel_tol=1e-3)
        self.assertTrue(result['cnc']['possible'])
        self.assertTrue(is_close)
