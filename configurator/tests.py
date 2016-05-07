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

    def test_calc__P10(self):
        bisec = BisecService(20, 20, 86)
        bisec.set_connector("P10")
        result = bisec.check()
        print("\nP10 Bisec: %s\n" % result)

        # CNC tests
        self.assertTrue(math.isclose(result['cnc']['position'], 9.894, rel_tol=1e-3))
        self.assertTrue(result['cnc']['possible'])

        # Zeta tests
        self.assertTrue(result['zeta']['0mm']['possible'])
        self.assertTrue(result['zeta']['2mm']['possible'])
        self.assertTrue(result['zeta']['4mm']['possible'])
        # TODO: Check values

    def test_calc_P14(self):
        bisec = BisecService(20, 20, 86)
        bisec.set_connector("P14")
        result = bisec.check()
        print("\nP14 Bisec: %s\n" % result)

        # CNC tests
        self.assertTrue(math.isclose(result['cnc']['position'], 7.749, rel_tol=1e-3))
        self.assertTrue(result['cnc']['possible'])

        # Zeta tests
        self.assertFalse(result['zeta']['0mm']['possible'])
        self.assertTrue(result['zeta']['2mm']['possible'])
        self.assertTrue(result['zeta']['4mm']['possible'])
        # TODO: Check values

    def test_calc_P1014(self):
        bisec = BisecService(20, 20, 86)
        bisec.set_connector("P1014")
        result = bisec.check()
        print("\nP1014 Bisec: %s\n" % result)

        # CNC tests
        self.assertTrue(math.isclose(result['cnc']['position'], 7.749, rel_tol=1e-3))
        self.assertTrue(result['cnc']['possible'])

        # Zeta tests
        self.assertFalse(result['zeta']['0mm']['possible'])
        self.assertTrue(result['zeta']['2mm']['possible'])
        self.assertTrue(result['zeta']['4mm']['possible'])
        # TODO: Check values


class StumbEdgeTest(TestCase):

    def setUp(self):
        p1 = Connector(name="P10", p1=8.46, p2=4.9, p3=10, p4=2.7)
        p1.save()
        p2 = Connector(name="P14", p1=12.46, p2=4.9, p3=14, p4=2.7)
        p2.save()
        p3 = Connector(name="P1014", p1=12.46, p2=4.9, p3=14, p4=2.7)
        p3.save()

    def test_calc__P10(self):
        stumb_edge = StumbEdgeService(20, 20, 86)
        stumb_edge.set_connector("P10")
        result = stumb_edge.check()
        print("\nP10 stumb_edge: %s\n" % result)

        # CNC tests
        self.assertTrue(math.isclose(result['cnc']['position'], 10.321, rel_tol=1e-3))
        self.assertTrue(result['cnc']['possible'])

        # Zeta tests
        self.assertTrue(result['zeta']['0mm']['possible'])
        self.assertTrue(result['zeta']['2mm']['possible'])
        self.assertTrue(result['zeta']['4mm']['possible'])
        # TODO: Check values

    def test_calc_P14(self):
        stumb_edge = StumbEdgeService(20, 20, 86)
        stumb_edge.set_connector("P14")
        result = stumb_edge.check()
        print("\nP14 stumb_edge: %s\n" % result)

        # CNC tests
        self.assertTrue(math.isclose(result['cnc']['position'], 10.461, rel_tol=1e-3))
        self.assertTrue(result['cnc']['possible'])

        # Zeta tests
        self.assertTrue(result['zeta']['0mm']['possible'])
        self.assertTrue(result['zeta']['2mm']['possible'])
        self.assertTrue(result['zeta']['4mm']['possible'])
        # TODO: Check values

    def test_calc_P1014(self):
        stumb_edge = StumbEdgeService(20, 20, 86)
        stumb_edge.set_connector("P1014")
        result = stumb_edge.check()
        print("\nP1014 stumb_edge: %s\n" % result)

        # CNC tests
        self.assertTrue(math.isclose(result['cnc']['position'], 10.461, rel_tol=1e-3))
        self.assertTrue(result['cnc']['possible'])

        # Zeta tests
        self.assertTrue(result['zeta']['0mm']['possible'])
        self.assertTrue(result['zeta']['2mm']['possible'])
        self.assertTrue(result['zeta']['4mm']['possible'])
        # TODO: Check values


class TConnectionTest(TestCase):

    def setUp(self):
        p1 = Connector(name="P10", p1=8.46, p2=4.9, p3=10, p4=2.7)
        p1.save()
        p2 = Connector(name="P14", p1=12.46, p2=4.9, p3=14, p4=2.7)
        p2.save()
        p3 = Connector(name="P1014", p1=12.46, p2=4.9, p3=14, p4=2.7)
        p3.save()

    def test_calc__P10(self):
        t_conn = TConnectionService(20, 20, 86)
        t_conn.set_connector("P10")
        result = t_conn.check()
        print("\nP10 t_conn: %s\n" % result)

        # CNC tests
        self.assertTrue(math.isclose(result['cnc']['position'], 10.321, rel_tol=1e-3))
        self.assertTrue(result['cnc']['possible'])

        # Zeta tests
        self.assertTrue(result['zeta']['0mm']['possible'])
        self.assertTrue(result['zeta']['2mm']['possible'])
        self.assertTrue(result['zeta']['4mm']['possible'])
        # TODO: Check values

    def test_calc_P14(self):
        t_conn = TConnectionService(20, 20, 86)
        t_conn.set_connector("P14")
        result = t_conn.check()
        print("\nP14 t_conn: %s\n" % result)

        # CNC tests
        self.assertTrue(math.isclose(result['cnc']['position'], 10.461, rel_tol=1e-3))
        self.assertTrue(result['cnc']['possible'])

        # Zeta tests
        self.assertTrue(result['zeta']['0mm']['possible'])
        self.assertTrue(result['zeta']['2mm']['possible'])
        self.assertTrue(result['zeta']['4mm']['possible'])
        # TODO: Check values

    def test_calc_P1014(self):
        t_conn = TConnectionService(20, 20, 86)
        t_conn.set_connector("P1014")
        result = t_conn.check()
        print("\nP1014 t_conn: %s\n" % result)

        # CNC tests
        self.assertTrue(math.isclose(result['cnc']['position'], 10.461, rel_tol=1e-3))
        self.assertTrue(result['cnc']['possible'])

        # Zeta tests
        self.assertTrue(result['zeta']['0mm']['possible'])
        self.assertTrue(result['zeta']['2mm']['possible'])
        self.assertTrue(result['zeta']['4mm']['possible'])
        # TODO: Check values


#class MiterConnectionTest(TestCase):
#
#    def setUp(self):
#        p1 = Connector(name="P10", p1=8.46, p2=4.9, p3=10, p4=2.7)
#        p1.save()
#        p2 = Connector(name="P14", p1=12.46, p2=4.9, p3=14, p4=2.7)
#        p2.save()
#        p3 = Connector(name="P1014", p1=12.46, p2=4.9, p3=14, p4=2.7)
#        p3.save()
#
#    def test_calc__P10(self):
#        miter_conn = MiterService(20, 20, 86)
#        miter_conn.set_connector("P10")
#        result = miter_conn.check()
#        print("\nP10 miter_conn: %s\n" % result)
#
#        # CNC tests
#        self.assertTrue(math.isclose(result['cnc']['position'], 10.321, rel_tol=1e-3))
#        self.assertFalse(result['cnc']['possible'])
#
#        # Zeta tests
#        self.assertFalse(result['zeta']['0mm']['possible'])
#        self.assertFalse(result['zeta']['2mm']['possible'])
#        self.assertFalse(result['zeta']['4mm']['possible'])
#        # TODO: Check values
#
#    def test_calc_P14(self):
#        miter_conn = MiterService(20, 20, 86)
#        miter_conn.set_connector("P14")
#        result = miter_conn.check()
#        print("\nP14 miter_conn: %s\n" % result)
#
#        # CNC tests
#        self.assertTrue(math.isclose(result['cnc']['position'], 10.461, rel_tol=1e-3))
#        self.assertFalse(result['cnc']['possible'])
#
#        # Zeta tests
#        self.assertFalse(result['zeta']['0mm']['possible'])
#        self.assertFalse(result['zeta']['2mm']['possible'])
#        self.assertFalse(result['zeta']['4mm']['possible'])
#        # TODO: Check values
#
#    def test_calc_P1014(self):
#        miter_conn = MiterService(20, 20, 86)
#        miter_conn.set_connector("P1014")
#        result = miter_conn.check()
#        print("\nP1014 miter_conn: %s\n" % result)
#
#        # CNC tests
#        self.assertTrue(math.isclose(result['cnc']['position'], 10.461, rel_tol=1e-3))
#        self.assertFalse(result['cnc']['possible'])
#
#        # Zeta tests
#        self.assertFalse(result['zeta']['0mm']['possible'])
#        self.assertFalse(result['zeta']['2mm']['possible'])
#        self.assertFalse(result['zeta']['4mm']['possible'])
#        # TODO: Check values
