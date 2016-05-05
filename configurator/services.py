import math
from .models import Connector


class ConnectorService:
    m1_width = 0
    m2_width = 0
    angle = 90
    gehrung = 0
    links = []
    rechts = []
    results = {}

    connector = None

    def __init__(self, m1_width, m2_width, angle):
        self.m1_width = m1_width
        self.m2_width = m2_width
        self.angle = angle

        self.gehrung = abs(90 - angle / 2)

        self.results['cnc'] = {}
        self.results['cnc']['possible'] = False
        self.results['cnc']['position'] = 0
        self.results['zeta'] = {}
        self.results['zeta']['0mm'] = {}
        self.results['zeta']['2mm'] = {}
        self.results['zeta']['4mm'] = {}
        self.results['zeta']['0mm']['possible'] = False
        self.results['zeta']['2mm']['possible'] = False
        self.results['zeta']['4mm']['possible'] = False
        self.results['zeta']['0mm']['val'] = 0
        self.results['zeta']['2mm']['val'] = 0
        self.results['zeta']['4mm']['val'] = 0

    @staticmethod
    def factory(type, m1_width, m2_width, angle):
        if type == "Stumb Edge": return StumbEdgeService(m1_width, m2_width, angle)
        if type == "Bisectrix": return BisecService(m1_width, m2_width, angle)
        if type == "T-Connection": return TConnectionService(m1_width, m2_width, angle)
        if type == "Miter": return MiterService(m1_width, m2_width, angle)

    def set_connector(self, connector_name):
        self.connector = Connector.objects.get(name=connector_name)

        if self.connector is None:
            raise RuntimeError("Please set a connector name!")

    def zeta_0mm(self):
        raise NotImplementedError("Please Implement this method")

    def zeta_2mm(self):
        raise NotImplementedError("Please Implement this method")

    def zeta_4mm(self):
        raise NotImplementedError("Please Implement this method")

    def check(self):
        raise NotImplementedError("Please Implement this method")


class BisecService(ConnectorService):

    def __init__(self, m1_width, m2_width, angle):
        ConnectorService.__init__(self, m1_width, m2_width, angle)
        self.links.append(5.9)

    def calc_h(self):
        kontaktdistanz = math.sqrt(((self.m2_width + self.m1_width / math.cos(self.angle / 180 * math.pi))
                                    / math.tan(self.angle / 180 * math.pi)) ** 2 + self.m2_width ** 2)

        schnittwinkel = 90 - math.degrees(math.acos(self.m2_width / kontaktdistanz))
        return self.calc(kontaktdistanz, schnittwinkel)

    def calc_v(self):
        kontaktdistanz = math.sqrt(((self.m2_width + self.m1_width / math.cos(self.angle / 180 * math.pi))
                                    / math.tan(self.angle / 180 * math.pi)) ** 2 + self.m2_width ** 2)

        schnittwinkel = 90 - math.degrees(math.acos(self.m1_width / kontaktdistanz))
        return self.calc(kontaktdistanz, schnittwinkel)

    def calc(self, kontaktdistanz, schnittwinkel):
        rechts_niedrig = (kontaktdistanz - (1 / math.cos(schnittwinkel / 180 * math.pi) + float(self.connector.p1))
                          / math.tan(schnittwinkel / 180 * math.pi) - float(self.connector.p2))
        rechts_hoch = (kontaktdistanz - (1 / math.cos(schnittwinkel / 180 * math.pi) + float(self.connector.p3))
                       / math.tan(schnittwinkel / 180 * math.pi) - float(self.connector.p4))

        rechts = rechts_niedrig if rechts_niedrig < rechts_hoch else rechts_hoch
        # FIXME: use right links!!
        space_range = rechts - self.links[0]
        position = (self.links[0] + rechts) / 2

        return {'rechts': rechts, 'range': space_range, 'position': position}

    def zeta_0mm(self):
        cond1 = (self.m1_width == self.m2_width)
        cond2 = (max(self.links) < 14 - (math.tan(self.gehrung / 180 * math.pi) * 4 / math.sin(self.gehrung / 180 * math.pi)
                 - math.tan(self.gehrung / 180 * math.pi) * 4))
        cond3 = ((14 - (math.tan(self.gehrung / 180 * math.pi) * 4 / math.sin(self.gehrung / 180 * math.pi) -
                 math.tan(self.gehrung / 180 * math.pi) * 4)) < min(self.rechts))

        return cond1 and cond2 and cond3

    def zeta_2mm(self):
        cond1 = (self.m1_width == self.m2_width)
        cond2 = (max(self.links) < 14 - ((math.tan(self.gehrung / 180 * math.pi) * 4 / math.sin(self.gehrung / 180 * math.pi)
                 - math.tan(self.gehrung / 180 * math.pi) * 4) + 2 / math.cos(self.gehrung / 180 * math.pi)))
        cond3 = (14 - ((math.tan(self.gehrung / 180 * math.pi) * 4 / math.sin(self.gehrung / 180 * math.pi) -
                 math.tan(self.gehrung / 180 * math.pi) * 4) + 2 / math.cos(self.gehrung / 180 * math.pi)) < min(self.rechts))

        return cond1 and cond2 and cond3

    def zeta_4mm(self):
        return self.zeta_2mm()

    def check(self):
        horizontal = self.calc_h()
        self.rechts.append(horizontal['rechts'])
        vertical = self.calc_v()
        self.rechts.append(vertical['rechts'])

        range_h = horizontal['range']
        range_v = vertical['range']

        if range_h > 0 and range_v > 0:
            self.results['cnc']['possible'] = True
            rechts_h = horizontal['rechts']
            rechts_v = vertical['rechts']
            # FIXME: What is links?
            self.results['cnc']['position'] = (max(self.links[0], self.links[0]) + min(rechts_v, rechts_h)) / 2

        self.results['zeta']['0mm']['possible'] = self.zeta_0mm()
        self.results['zeta']['2mm']['possible'] = self.zeta_2mm()
        self.results['zeta']['4mm']['possible'] = self.zeta_4mm()

        return self.results


class StumbEdgeService(ConnectorService):

    def __init__(self, m1_width, m2_width, angle):
        ConnectorService.__init__(self, m1_width, m2_width, angle)
        self.links.append(5.9)

    def calc(self):
        kontaktdistanz = math.sqrt(((self.m2_width + self.m1_width / math.cos(self.angle / 180 * math.pi))
                                    / math.tan(self.angle / 180 * math.pi)) ** 2 + self.m2_width ** 2)

        schnittwinkel = 90 - math.degrees(math.acos(self.m2_width / kontaktdistanz))
        rechts_niedrig = (kontaktdistanz - (1 / math.cos(schnittwinkel / 180 * math.pi) + float(self.connector.p1))
                          / math.tan(schnittwinkel / 180 * math.pi) - float(self.connector.p2))
        rechts_hoch = (kontaktdistanz - (1 / math.cos(schnittwinkel / 180 * math.pi) + float(self.connector.p3))
                       / math.tan(schnittwinkel / 180 * math.pi) - float(self.connector.p4))

        rechts = rechts_niedrig if rechts_niedrig < rechts_hoch else rechts_hoch
        # FIXME: use right links!!
        space_range = rechts - self.links[0]
        position = (self.links[0] + rechts) / 2

        return {'rechts': rechts, 'range': space_range, 'position': position}

    def zeta_0mm(self):
        cond1 = self.m1_width > 11

        if self.angle >= 90:
            cond2 = (max(self.links) < 14 - (math.tan(self.gehrung / 180 * math.pi) * 4 / math.sin(self.gehrung / 180 * math.pi)
                     - math.tan(self.gehrung / 180 * math.pi) * 4))
            cond3 = ((14 - (math.tan(self.gehrung / 180 * math.pi) * 4 / math.sin(self.gehrung / 180 * math.pi) -
                     math.tan(self.gehrung / 180 * math.pi) * 4)) < min(self.rechts))
        else:
            cond2 = True
            cond3 = True

        return cond1 and cond2 and cond3

    def zeta_2mm(self):
        cond1 = (self.m1_width == self.m2_width)

        if self.angle >= 90:
            cond2 = (max(self.links) < 14 - ((math.tan(self.gehrung / 180 * math.pi) * 4 / math.sin(self.gehrung / 180 * math.pi)
                     - math.tan(self.gehrung / 180 * math.pi) * 4) + 2 / math.cos(self.gehrung / 180 * math.pi)))
            cond3 = (14 - ((math.tan(self.gehrung / 180 * math.pi) * 4 / math.sin(self.gehrung / 180 * math.pi) -
                     math.tan(self.gehrung / 180 * math.pi) * 4) + 2 / math.cos(self.gehrung / 180 * math.pi)) < min(self.rechts))
        else:
            cond2 = True
            cond3 = True

        return cond1 and cond2 and cond3

    def zeta_4mm(self):
        return self.zeta_2mm()

    def check(self):
        variables = self.calc()
        self.rechts.append(variables['rechts'])

        range_lr = variables['range']

        if range_lr > 0:
            self.results['cnc']['possible'] = True
            rechts = variables['rechts']
            # FIXME: What is links?
            self.results['cnc']['position'] = (max(self.links[0], self.links[0]) + min(rechts)) / 2

        self.results['zeta']['0mm']['possible'] = self.zeta_0mm()
        self.results['zeta']['2mm']['possible'] = self.zeta_2mm()
        self.results['zeta']['4mm']['possible'] = self.zeta_4mm()

        return self.results


class TConnectionService(ConnectorService):

    def __init__(self, m1_width, m2_width, angle):
        ConnectorService.__init__(self, m1_width, m2_width, angle)
        self.links.append(5.9)


class MiterService(ConnectorService):

    def __init__(self, m1_width, m2_width, angle):
        ConnectorService.__init__(self, m1_width, m2_width, angle)
        self.links.append(5.9)
