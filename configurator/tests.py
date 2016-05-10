from django.test import TestCase
from .services import BisecService, StumbEdgeService, TConnectionService, MiterService
from .models import Connector
import math


class BisecTest(TestCase):

    def setUp(self):
        p1 = Connector(name="P10", p1=8.46, p2=4.9, p3=10, p4=2.7)
        p1.save()
        p2 = Connector(name="P14", p1=12.46, p2=4.9, p3=14, p4=2.7)
        p2.save()
        p3 = Connector(name="P1014", p1=12.46, p2=4.9, p3=14, p4=2.7)
        p3.save()

    def test_calc_smaller90_P10(self):
        bisec = BisecService(20, 20, 86)
        bisec.set_connector("P10")
        result = bisec.check()

        # CNC tests
        self.assertAlmostEqual(result['cnc']['position'], 9.894, places=3, msg=None, delta=None)
        self.assertTrue(result['cnc']['possible'])

        # Zeta tests
        self.assertTrue(result['zeta']['0mm']['possible'])
        self.assertTrue(result['zeta']['2mm']['possible'])
        self.assertTrue(result['zeta']['4mm']['possible'])

        # TODO: Check values
        self.assertAlmostEqual(result['zeta']['0mm']['val'], 0.00, places=3, msg=None, delta=None)
        self.assertAlmostEqual(result['zeta']['2mm']['val'], 0.00, places=3, msg=None, delta=None)
        self.assertAlmostEqual(result['zeta']['4mm']['val'], 0.00, places=3, msg=None, delta=None)

    def test_calc_bigger90_P10(self):
        bisec = BisecService(20, 20, 110)
        bisec.set_connector("P10")
        result = bisec.check()

        # CNC tests
        self.assertAlmostEqual(result['cnc']['position'], 9.135, places=3, msg=None, delta=None)
        self.assertTrue(result['cnc']['possible'])

        # Zeta tests
        self.assertTrue(result['zeta']['0mm']['possible'])
        self.assertTrue(result['zeta']['2mm']['possible'])
        self.assertTrue(result['zeta']['4mm']['possible'])

        # TODO: Check values
        self.assertAlmostEqual(result['zeta']['0mm']['val'], 0.00, places=3, msg=None, delta=None)
        self.assertAlmostEqual(result['zeta']['2mm']['val'], 0.00, places=3, msg=None, delta=None)
        self.assertAlmostEqual(result['zeta']['4mm']['val'], 0.00, places=3, msg=None, delta=None)

    def test_calc_smaller90P14(self):
        bisec = BisecService(20, 20, 86)
        bisec.set_connector("P14")
        result = bisec.check()

        # CNC tests
        self.assertAlmostEqual(result['cnc']['position'], 7.749, places=3, msg=None, delta=None)
        self.assertTrue(result['cnc']['possible'])

        # Zeta tests
        self.assertFalse(result['zeta']['0mm']['possible'])
        self.assertTrue(result['zeta']['2mm']['possible'])
        self.assertTrue(result['zeta']['4mm']['possible'])

        # TODO: Check values
        self.assertAlmostEqual(result['zeta']['0mm']['val'], 0.00, places=3, msg=None, delta=None)
        self.assertAlmostEqual(result['zeta']['2mm']['val'], 0.00, places=3, msg=None, delta=None)
        self.assertAlmostEqual(result['zeta']['4mm']['val'], 0.00, places=3, msg=None, delta=None)

    def test_calc_smaller90P1014(self):
        bisec = BisecService(20, 20, 86)
        bisec.set_connector("P1014")
        result = bisec.check()

        # CNC tests
        self.assertAlmostEqual(result['cnc']['position'], 7.749, places=3, msg=None, delta=None)
        self.assertTrue(result['cnc']['possible'])

        # Zeta tests
        self.assertFalse(result['zeta']['0mm']['possible'])
        self.assertTrue(result['zeta']['2mm']['possible'])
        self.assertTrue(result['zeta']['4mm']['possible'])

        # TODO: Check values
        self.assertAlmostEqual(result['zeta']['0mm']['val'], 0.00, places=3, msg=None, delta=None)
        self.assertAlmostEqual(result['zeta']['2mm']['val'], 0.00, places=3, msg=None, delta=None)
        self.assertAlmostEqual(result['zeta']['4mm']['val'], 0.00, places=3, msg=None, delta=None)


class StumbEdgeTest(TestCase):

    def setUp(self):
        p1 = Connector(name="P10", p1=8.46, p2=4.9, p3=10, p4=2.7)
        p1.save()
        p2 = Connector(name="P14", p1=12.46, p2=4.9, p3=14, p4=2.7)
        p2.save()
        p3 = Connector(name="P1014", p1=12.46, p2=4.9, p3=14, p4=2.7)
        p3.save()

    def test_calc_smaller90_P10(self):
        stumb_edge = StumbEdgeService(20, 20, 86)
        stumb_edge.set_connector("P10")
        result = stumb_edge.check()

        # CNC tests
        self.assertAlmostEqual(result['cnc']['position'], 10.321, places=3, msg=None, delta=None)
        self.assertTrue(result['cnc']['possible'])

        # Zeta tests
        self.assertTrue(result['zeta']['0mm']['possible'])
        self.assertTrue(result['zeta']['2mm']['possible'])
        self.assertTrue(result['zeta']['4mm']['possible'])

        # TODO: Check values
        self.assertAlmostEqual(result['zeta']['0mm']['val'][0], 10.27, places=2, msg=None, delta=None)
        self.assertAlmostEqual(result['zeta']['2mm']['val'][0], 8.27, places=2, msg=None, delta=None)
        self.assertAlmostEqual(result['zeta']['4mm']['val'][0], 6.26, places=2, msg=None, delta=None)

    def test_calc_bigger90_P10(self):
        stumb_edge = StumbEdgeService(20, 20, 110)
        stumb_edge.set_connector("P10")
        result = stumb_edge.check()

        # CNC tests
        self.assertAlmostEqual(result['cnc']['position'], 10.642, places=3, msg=None, delta=None)
        self.assertTrue(result['cnc']['possible'])

        # Zeta tests
        self.assertTrue(result['zeta']['0mm']['possible'])
        self.assertTrue(result['zeta']['2mm']['possible'])
        self.assertTrue(result['zeta']['4mm']['possible'])

        # TODO: Check values
        self.assertAlmostEqual(result['zeta']['0mm']['val'][0], 11.199, places=2, msg=None, delta=None)
        self.assertAlmostEqual(result['zeta']['2mm']['val'][0], 9.07, places=2, msg=None, delta=None)
        self.assertAlmostEqual(result['zeta']['4mm']['val'][0], 6.94, places=2, msg=None, delta=None)

    def test_calc_smaller90P14(self):
        stumb_edge = StumbEdgeService(20, 20, 86)
        stumb_edge.set_connector("P14")
        result = stumb_edge.check()

        # CNC tests
        self.assertAlmostEqual(result['cnc']['position'], 10.461, places=3, msg=None, delta=None)
        self.assertTrue(result['cnc']['possible'])

        # Zeta tests
        self.assertTrue(result['zeta']['0mm']['possible'])
        self.assertTrue(result['zeta']['2mm']['possible'])
        self.assertTrue(result['zeta']['4mm']['possible'])

        # TODO: Check values
        self.assertAlmostEqual(result['zeta']['0mm']['val'][0], 10.27, places=2, msg=None, delta=None)
        self.assertAlmostEqual(result['zeta']['2mm']['val'][0], 8.27, places=2, msg=None, delta=None)
        self.assertAlmostEqual(result['zeta']['4mm']['val'][0], 6.26, places=2, msg=None, delta=None)

    def test_calc_smaller90P1014(self):
        stumb_edge = StumbEdgeService(20, 20, 86)
        stumb_edge.set_connector("P1014")
        result = stumb_edge.check()

        # CNC tests
        self.assertAlmostEqual(result['cnc']['position'], 10.461, places=3, msg=None, delta=None)
        self.assertTrue(result['cnc']['possible'])

        # Zeta tests
        self.assertTrue(result['zeta']['0mm']['possible'])
        self.assertTrue(result['zeta']['2mm']['possible'])
        self.assertTrue(result['zeta']['4mm']['possible'])

        # TODO: Check values
        self.assertAlmostEqual(result['zeta']['0mm']['val'][0], 10.27, places=2, msg=None, delta=None)
        self.assertAlmostEqual(result['zeta']['2mm']['val'][0], 8.27, places=2, msg=None, delta=None)
        self.assertAlmostEqual(result['zeta']['4mm']['val'][0], 6.26, places=2, msg=None, delta=None)


class TConnectionTest(TestCase):

    def setUp(self):
        p1 = Connector(name="P10", p1=8.46, p2=4.9, p3=10, p4=2.7)
        p1.save()
        p2 = Connector(name="P14", p1=12.46, p2=4.9, p3=14, p4=2.7)
        p2.save()
        p3 = Connector(name="P1014", p1=12.46, p2=4.9, p3=14, p4=2.7)
        p3.save()

    def test_calc_smaller90_P10(self):
        t_conn = TConnectionService(20, 20, 86)
        t_conn.set_connector("P10")
        result = t_conn.check()

        # CNC tests
        self.assertAlmostEqual(result['cnc']['position'], 10.321, places=3, msg=None, delta=None)
        self.assertTrue(result['cnc']['possible'])

        # Zeta tests
        self.assertTrue(result['zeta']['0mm']['possible'])
        self.assertTrue(result['zeta']['2mm']['possible'])
        self.assertTrue(result['zeta']['4mm']['possible'])

        # TODO: Check values
        self.assertAlmostEqual(result['zeta']['0mm']['val'], 0.00, places=3, msg=None, delta=None)
        self.assertAlmostEqual(result['zeta']['2mm']['val'], 0.00, places=3, msg=None, delta=None)
        self.assertAlmostEqual(result['zeta']['4mm']['val'], 0.00, places=3, msg=None, delta=None)

    def test_calc_bigger90_P10(self):
        t_conn = TConnectionService(20, 20, 110)
        t_conn.set_connector("P10")
        result = t_conn.check()

        # CNC tests
        self.assertAlmostEqual(result['cnc']['position'], 9.070, places=3, msg=None, delta=None)
        self.assertTrue(result['cnc']['possible'])

        # Zeta tests
        self.assertTrue(result['zeta']['0mm']['possible'])
        self.assertTrue(result['zeta']['2mm']['possible'])
        self.assertTrue(result['zeta']['4mm']['possible'])

        # TODO: Check values
        self.assertAlmostEqual(result['zeta']['0mm']['val'], 0.00, places=3, msg=None, delta=None)
        self.assertAlmostEqual(result['zeta']['2mm']['val'], 0.00, places=3, msg=None, delta=None)
        self.assertAlmostEqual(result['zeta']['4mm']['val'], 0.00, places=3, msg=None, delta=None)

    def test_calc_smaller90P14(self):
        t_conn = TConnectionService(20, 20, 86)
        t_conn.set_connector("P14")
        result = t_conn.check()

        # CNC tests
        self.assertAlmostEqual(result['cnc']['position'], 10.461, places=3, msg=None, delta=None)
        self.assertTrue(result['cnc']['possible'])

        # Zeta tests
        self.assertTrue(result['zeta']['0mm']['possible'])
        self.assertTrue(result['zeta']['2mm']['possible'])
        self.assertTrue(result['zeta']['4mm']['possible'])

        # TODO: Check values
        self.assertAlmostEqual(result['zeta']['0mm']['val'], 0.00, places=3, msg=None, delta=None)
        self.assertAlmostEqual(result['zeta']['2mm']['val'], 0.00, places=3, msg=None, delta=None)
        self.assertAlmostEqual(result['zeta']['4mm']['val'], 0.00, places=3, msg=None, delta=None)

    def test_calc_smaller90P1014(self):
        t_conn = TConnectionService(20, 20, 86)
        t_conn.set_connector("P1014")
        result = t_conn.check()

        # CNC tests
        self.assertAlmostEqual(result['cnc']['position'], 10.461, places=3, msg=None, delta=None)
        self.assertTrue(result['cnc']['possible'])

        # Zeta tests
        self.assertTrue(result['zeta']['0mm']['possible'])
        self.assertTrue(result['zeta']['2mm']['possible'])
        self.assertTrue(result['zeta']['4mm']['possible'])

        # TODO: Check values
        self.assertAlmostEqual(result['zeta']['0mm']['val'], 0.00, places=3, msg=None, delta=None)
        self.assertAlmostEqual(result['zeta']['2mm']['val'], 0.00, places=3, msg=None, delta=None)
        self.assertAlmostEqual(result['zeta']['4mm']['val'], 0.00, places=3, msg=None, delta=None)


# class MiterConnectionTest(TestCase):
#
#    def setUp(self):
#        p1 = Connector(name="P10", p1=8.46, p2=4.9, p3=10, p4=2.7)
#        p1.save()
#        p2 = Connector(name="P14", p1=12.46, p2=4.9, p3=14, p4=2.7)
#        p2.save()
#        p3 = Connector(name="P1014", p1=12.46, p2=4.9, p3=14, p4=2.7)
#        p3.save()
#
#    def test_calc_smaller90_P10(self):
#        miter_conn = MiterService(20, 20, 86)
#        miter_conn.set_connector("P10")
#        result = miter_conn.check()
#
#        # CNC tests
#        self.assertAlmostEqual(result['cnc']['position'], 10.321, places=3, msg=None, delta=None)
#        self.assertFalse(result['cnc']['possible'])
#
#        # Zeta tests
#        self.assertFalse(result['zeta']['0mm']['possible'])
#        self.assertFalse(result['zeta']['2mm']['possible'])
#        self.assertFalse(result['zeta']['4mm']['possible'])
#        # TODO: Check values
#
#    def test_calc_smaller90P14(self):
#        miter_conn = MiterService(20, 20, 86)
#        miter_conn.set_connector("P14")
#        result = miter_conn.check()
#
#        # CNC tests
#        self.assertAlmostEqual(result['cnc']['position'], 10.461, places=3, msg=None, delta=None)
#        self.assertFalse(result['cnc']['possible'])
#
#        # Zeta tests
#        self.assertFalse(result['zeta']['0mm']['possible'])
#        self.assertFalse(result['zeta']['2mm']['possible'])
#        self.assertFalse(result['zeta']['4mm']['possible'])
#        # TODO: Check values
#
#    def test_calc_smaller90P1014(self):
#        miter_conn = MiterService(20, 20, 86)
#        miter_conn.set_connector("P1014")
#        result = miter_conn.check()
#
#        # CNC tests
#        self.assertAlmostEqual(result['cnc']['position'], 10.461, places=3, msg=None, delta=None)
#        self.assertFalse(result['cnc']['possible'])
#
#        # Zeta tests
#        self.assertFalse(result['zeta']['0mm']['possible'])
#        self.assertFalse(result['zeta']['2mm']['possible'])
#        self.assertFalse(result['zeta']['4mm']['possible'])
#        # TODO: Check values
