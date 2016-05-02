from django.test import TestCase
from .services import BisecService
from .models import Connector
import math


class ServicesTestCase(TestCase):

    def setUp(self):
        p1 = Connector(name="P10", p1=8.46, p2=4.9, p3=10, p4=2.7)
        p1.save()
        p2 = Connector(name="P14", p1=8.46, p2=4.9, p3=10, p4=2.7)
        p2.save()
        p3 = Connector(name="P1014", p1=8.46, p2=4.9, p3=10, p4=2.7)
        p3.save()

    def test_calc_bisec(self):
        m1 = 20
        m2 = 17
        angle = 90

        bisec = BisecService(m1, m2, angle)
        bisec.set_connector("P10")
        result = bisec.check()
        print(result)
        is_close = math.isclose(result['cnc']['position'], 7.87, rel_tol=1e-3)
        self.assertTrue(result['cnc']['possible'])
        self.assertTrue(is_close)
