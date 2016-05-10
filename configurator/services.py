import math
from .models import Connector


class ConnectorService:
    m1_width = 0
    m2_width = 0
    angle = 90
    gehrung = 0
    stumb = 0

    links_max = 5.9
    links = []
    rechts = []

    results = {}

    connector = None

    def __init__(self, m1_width, m2_width, angle):
        self.m1_width = m1_width
        self.m2_width = m2_width
        self.angle = angle
        self.links = []
        self.rechts = []

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

        if self.angle == 90 or self.angle == 180 or self.angle == 0:
            self.stumb = 0.0000000001
        else:
            self.stumb = abs(90 - self.angle)

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
        space_range = rechts - self.links_max
        position = (self.links_max + rechts) / 2

        return {'links': self.links_max, 'rechts': rechts, 'range': space_range, 'position': position}

    def zeta_0mm(self):
        cond1 = (self.m1_width == self.m2_width)
        cond2 = (self.links_max < 14 - (math.tan(self.gehrung / 180 * math.pi) * 4 / math.sin(self.gehrung / 180 * math.pi)
                 - math.tan(self.gehrung / 180 * math.pi) * 4))
        cond3 = ((14 - (math.tan(self.gehrung / 180 * math.pi) * 4 / math.sin(self.gehrung / 180 * math.pi) -
                 math.tan(self.gehrung / 180 * math.pi) * 4)) < min(self.rechts))

        return cond1 and cond2 and cond3

    def zeta_2mm(self):
        cond1 = (self.m1_width == self.m2_width)
        cond2 = (self.links_max < 14 - ((math.tan(self.gehrung / 180 * math.pi) * 4 / math.sin(self.gehrung / 180 * math.pi)
                 - math.tan(self.gehrung / 180 * math.pi) * 4) + 2 / math.cos(self.gehrung / 180 * math.pi)))
        cond3 = (14 - ((math.tan(self.gehrung / 180 * math.pi) * 4 / math.sin(self.gehrung / 180 * math.pi) -
                 math.tan(self.gehrung / 180 * math.pi) * 4) + 2 / math.cos(self.gehrung / 180 * math.pi)) < min(self.rechts))

        return cond1 and cond2 and cond3

    def zeta_4mm(self):
        return self.zeta_2mm()

    def check(self):
        horizontal = self.calc_h()
        vertical = self.calc_v()
        self.links.append(horizontal['links'])
        self.links.append(vertical['links'])
        self.rechts.append(horizontal['rechts'])
        self.rechts.append(vertical['rechts'])

        range_h = horizontal['range']
        range_v = vertical['range']

        if range_h > 0 and range_v > 0:
            self.results['cnc']['possible'] = True
            self.results['cnc']['position'] = (self.links_max + min(self.rechts)) / 2

        self.results['zeta']['0mm']['possible'] = self.zeta_0mm()
        self.results['zeta']['2mm']['possible'] = self.zeta_2mm()
        self.results['zeta']['4mm']['possible'] = self.zeta_4mm()

        return self.results


class StumbEdgeService(ConnectorService):

    def __init__(self, m1_width, m2_width, angle):
        ConnectorService.__init__(self, m1_width, m2_width, angle)

    def calc_schmalfl(self):
        kontaktdistanz = self.m2_width / math.sin(self.angle / 180 * math.pi)

        schnittwinkel = self.angle if self.angle <= 90 else 180 - self.angle

        rechts_niedrig = ((1 / math.cos(schnittwinkel / 180 * math.pi) + float(self.connector.p1))
                          / math.tan(schnittwinkel / 180 * math.pi) + float(self.connector.p2))
        rechts_hoch = ((1 / math.cos(schnittwinkel / 180 * math.pi) + float(self.connector.p3))
                       / math.tan(schnittwinkel / 180 * math.pi) + float(self.connector.p4))

        if self.angle >= 90:
            links = self.links_max
            if kontaktdistanz - rechts_niedrig < kontaktdistanz - rechts_hoch:
                rechts = kontaktdistanz - rechts_niedrig
            else:
                rechts = kontaktdistanz - rechts_hoch
        else:
            links = rechts_niedrig if rechts_niedrig > rechts_hoch else rechts_hoch
            rechts = kontaktdistanz - 5.9
        space_range = rechts - links
        position = (links + rechts) / 2

        return {'links': links, 'rechts': rechts, 'range': space_range, 'position': position}

    def calc_fl(self):
        kontaktdistanz = self.m2_width / math.sin(self.angle / 180 * math.pi)

        schnittwinkel = self.angle if self.angle <= 90 else 180 - self.angle

        rechts_niedrig = ((1 / math.cos(schnittwinkel / 180 * math.pi) + float(self.connector.p1))
                          / math.tan(schnittwinkel / 180 * math.pi) + float(self.connector.p2))
        rechts_hoch = ((1 / math.cos(schnittwinkel / 180 * math.pi) + float(self.connector.p3))
                       / math.tan(schnittwinkel / 180 * math.pi) + float(self.connector.p4))

        if self.angle >= 90:
            links = ((1 / math.cos(schnittwinkel / 180 * math.pi) + float(self.connector.p1))
                     / math.tan(schnittwinkel / 180 * math.pi) + float(self.connector.p2))
            if kontaktdistanz - rechts_niedrig < kontaktdistanz - rechts_hoch:
                rechts = kontaktdistanz - rechts_niedrig
            else:
                rechts = kontaktdistanz - rechts_hoch
        else:
            links = rechts_niedrig if rechts_niedrig > rechts_hoch else rechts_hoch
            rechts = kontaktdistanz - 5.9
        space_range = rechts - links
        position = (links + rechts) / 2

        return {'links': links, 'rechts': rechts, 'range': space_range, 'position': position}

    def zeta_0mm(self):
        kontaktdistanz = self.m2_width / math.sin(self.angle / 180 * math.pi)
        cond1 = self.m1_width > 11

        val1 = (14 - (math.tan(self.stumb / 180 * math.pi) * 4 /
                math.sin(self.stumb / 180 * math.pi) - math.tan(self.stumb / 180 * math.pi) * 4))
        val2 = (kontaktdistanz - (14 - (math.tan(self.stumb / 180 * math.pi) * 4 /
                math.sin(self.stumb / 180 * math.pi) - math.tan(self.stumb / 180 * math.pi) * 4)))

        cond2 = (max(self.links) < val2)
        cond3 = (val1 < min(self.rechts))

        return {'possible': cond1 and cond2 and cond3, 'val': [val1, val2]}

    def zeta_2mm(self):
        kontaktdistanz = self.m2_width / math.sin(self.angle / 180 * math.pi)
        cond1 = self.m1_width > 11

        val1 = (14 - ((math.tan(self.stumb / 180 * math.pi) * 4 /
                math.sin(self.stumb / 180 * math.pi) - math.tan(self.stumb / 180 * math.pi) * 4) + 2 / math.cos(self.stumb / 180 * math.pi)))
        val2 = (kontaktdistanz - (14 - ((math.tan(self.stumb / 180 * math.pi) * 4 /
                math.sin(self.stumb / 180 * math.pi) - math.tan(self.stumb / 180 * math.pi) * 4) + 2 / math.cos(self.stumb / 180 * math.pi))))

        cond2 = (max(self.links) < val2)
        cond3 = (val1 < min(self.rechts))

        return {'possible': cond1 and cond2 and cond3, 'val': [val1, val2]}

    def zeta_4mm(self):
        kontaktdistanz = self.m2_width / math.sin(self.angle / 180 * math.pi)
        cond1 = self.m1_width > 11

        val1 = (14 - ((math.tan(self.stumb / 180 * math.pi) * 4 /
                math.sin(self.stumb / 180 * math.pi) - math.tan(self.stumb / 180 * math.pi) * 4) + 4 / math.cos(self.stumb / 180 * math.pi)))
        val2 = (kontaktdistanz - (14 - ((math.tan(self.stumb / 180 * math.pi) * 4 /
                math.sin(self.stumb / 180 * math.pi) - math.tan(self.stumb / 180 * math.pi) * 4) + 4 / math.cos(self.stumb / 180 * math.pi))))

        cond2 = (max(self.links) < val2)
        cond3 = (val1 < min(self.rechts))

        return {'possible': cond1 and cond2 and cond3, 'val': [val1, val2]}

    def check(self):
        schmalfl = self.calc_schmalfl()
        fl = self.calc_fl()
        self.links.append(schmalfl['links'])
        self.links.append(fl['links'])
        self.rechts.append(schmalfl['rechts'])
        self.rechts.append(fl['rechts'])

        range_schmalfl = schmalfl['range']

        tmp_cnc = (max(self.links) + min(self.rechts)) / 2
        if tmp_cnc > range_schmalfl and tmp_cnc >= max(self.links) and tmp_cnc <= min(self.rechts):
            self.results['cnc']['possible'] = True
            self.results['cnc']['position'] = tmp_cnc

        self.results['zeta']['0mm'] = self.zeta_0mm()
        self.results['zeta']['2mm'] = self.zeta_2mm()
        self.results['zeta']['4mm'] = self.zeta_4mm()

        return self.results


# FIXME: Same as Stumb Edge?
# class TConnectionService(ConnectorService):
#
#    def __init__(self, m1_width, m2_width, angle):
#        ConnectorService.__init__(self, m1_width, m2_width, angle)
#
#    def calc_schmalfl(self):
#        kontaktdistanz = self.m2_width / math.sin(self.angle / 180 * math.pi)
#
#        schnittwinkel = self.angle if self.angle <= 90 else 180 - self.angle
#
#        rechts_niedrig = ((1 / math.cos(schnittwinkel / 180 * math.pi) + float(self.connector.p1))
#                          / math.tan(schnittwinkel / 180 * math.pi) + float(self.connector.p2))
#        rechts_hoch = ((1 / math.cos(schnittwinkel / 180 * math.pi) + float(self.connector.p3))
#                       / math.tan(schnittwinkel / 180 * math.pi) + float(self.connector.p4))
#
#        if self.angle >= 90:
#            links = self.links_max
#            if kontaktdistanz - rechts_niedrig < kontaktdistanz - rechts_hoch:
#                rechts = kontaktdistanz - rechts_niedrig
#            else:
#                rechts = kontaktdistanz - rechts_hoch
#        else:
#            links = rechts_niedrig if rechts_niedrig > rechts_hoch else rechts_hoch
#            rechts = kontaktdistanz - 5.9
#        space_range = rechts - links
#        position = (links + rechts) / 2
#
#        return {'links': links, 'rechts': rechts, 'range': space_range, 'position': position}
#
#    def calc_fl(self):
#        kontaktdistanz = self.m2_width / math.sin(self.angle / 180 * math.pi)
#
#        schnittwinkel = self.angle if self.angle <= 90 else 180 - self.angle
#
#        rechts_niedrig = ((1 / math.cos(schnittwinkel / 180 * math.pi) + float(self.connector.p1))
#                          / math.tan(schnittwinkel / 180 * math.pi) + float(self.connector.p2))
#        rechts_hoch = ((1 / math.cos(schnittwinkel / 180 * math.pi) + float(self.connector.p3))
#                       / math.tan(schnittwinkel / 180 * math.pi) + float(self.connector.p4))
#
#        if self.angle >= 90:
#            links = self.links_max
#            if kontaktdistanz - rechts_niedrig < kontaktdistanz - rechts_hoch:
#                rechts = kontaktdistanz - rechts_niedrig
#            else:
#                rechts = kontaktdistanz - rechts_hoch
#        else:
#            links = rechts_niedrig if rechts_niedrig > rechts_hoch else rechts_hoch
#            rechts = kontaktdistanz - 5.9
#        space_range = rechts - links
#        position = (links + rechts) / 2
#
#        return {'links': links, 'rechts': rechts, 'range': space_range, 'position': position}
#
#    def zeta_0mm(self):
#        kontaktdistanz = self.m2_width / math.sin(self.angle / 180 * math.pi)
#        cond1 = self.m1_width > 11
#
#        if self.angle >= 90:
#            cond2 = (max(self.links) < 14 - (math.tan(self.gehrung / 180 * math.pi) * 4 / math.sin(self.gehrung / 180 * math.pi)
#                     - math.tan(self.gehrung / 180 * math.pi) * 4))
#            cond3 = ((14 - (math.tan(self.gehrung / 180 * math.pi) * 4 / math.sin(self.gehrung / 180 * math.pi) -
#                     math.tan(self.gehrung / 180 * math.pi) * 4)) < min(self.rechts))
#        else:
#            cond2 = (max(self.links) < kontaktdistanz - (14 - (math.tan(self.gehrung / 180 * math.pi) * 4 / math.sin(self.gehrung / 180 * math.pi)
#                     - math.tan(self.gehrung / 180 * math.pi) * 4)))
#            # Check
#            cond3 = (kontaktdistanz - (14 - (math.tan(self.gehrung / 180 * math.pi) * 4 / math.sin(self.gehrung / 180 * math.pi) -
#                     math.tan(self.gehrung / 180 * math.pi) * 4)) < min(self.rechts))
#
#        return cond1 and cond2 and cond3
#
#    def zeta_2mm(self):
#        kontaktdistanz = self.m2_width / math.sin(self.angle / 180 * math.pi)
#        cond1 = self.m1_width > 11
#
#        if self.angle >= 90:
#            cond2 = (max(self.links) < 14 - ((math.tan(self.gehrung / 180 * math.pi) * 4 / math.sin(self.gehrung / 180 * math.pi)
#                     - math.tan(self.gehrung / 180 * math.pi) * 4) + 2 / math.cos(self.gehrung / 180 * math.pi)))
#            cond3 = (14 - ((math.tan(self.gehrung / 180 * math.pi) * 4 / math.sin(self.gehrung / 180 * math.pi) -
#                     math.tan(self.gehrung / 180 * math.pi) * 4) + 2 / math.cos(self.gehrung / 180 * math.pi)) < min(self.rechts))
#        else:
#            cond2 = (max(self.links) < kontaktdistanz - (14 - ((math.tan(self.gehrung / 180 * math.pi) * 4 / math.sin(self.gehrung / 180 * math.pi)
#                     - math.tan(self.gehrung / 180 * math.pi) * 4) + 2 / math.cos(self.gehrung / 180 * math.pi))))
#            cond3 = (kontaktdistanz - (14 - ((math.tan(self.gehrung / 180 * math.pi) * 4 / math.sin(self.gehrung / 180 * math.pi) -
#                     math.tan(self.gehrung / 180 * math.pi) * 4) + 2 / math.cos(self.gehrung / 180 * math.pi))) < min(self.rechts))
#
#        return cond1 and cond2 and cond3
#
#    def zeta_4mm(self):
#        return self.zeta_2mm()
#
#    def check(self):
#        schmalfl = self.calc_schmalfl()
#        fl = self.calc_fl()
#        self.links.append(schmalfl['links'])
#        self.links.append(fl['links'])
#        self.rechts.append(schmalfl['rechts'])
#        self.rechts.append(fl['rechts'])
#
#        range_schmalfl = schmalfl['range']
#
#        tmp_cnc = (max(self.links) + min(self.rechts)) / 2
#        if tmp_cnc > range_schmalfl and tmp_cnc >= max(self.links) and tmp_cnc <= min(self.rechts):
#            self.results['cnc']['possible'] = True
#            self.results['cnc']['position'] = tmp_cnc
#
#        self.results['zeta']['0mm']['possible'] = self.zeta_0mm()
#        self.results['zeta']['2mm']['possible'] = self.zeta_2mm()
#        self.results['zeta']['4mm']['possible'] = self.zeta_4mm()
#
#        return self.results


class MiterService(ConnectorService):

    def __init__(self, m1_width, m2_width, angle):
        ConnectorService.__init__(self, m1_width, m2_width, angle)

    def calc_schmalfl(self):
        kontaktdistanz = self.m2_width / math.sin(self.angle / 180 * math.pi)

        schnittwinkel = self.angle
        rechts_niedrig = ((1 / math.cos(schnittwinkel / 180 * math.pi) + float(self.connector.p1))
                          / math.tan(schnittwinkel / 180 * math.pi) + float(self.connector.p2))
        rechts_hoch = ((1 / math.cos(schnittwinkel / 180 * math.pi) + float(self.connector.p3))
                       / math.tan(schnittwinkel / 180 * math.pi) + float(self.connector.p4))

        if self.angle >= 90:
            links = self.links_max
            if kontaktdistanz - rechts_niedrig < kontaktdistanz - rechts_hoch:
                rechts = kontaktdistanz - rechts_niedrig
            else:
                rechts = kontaktdistanz - rechts_hoch
        else:
            links = rechts_niedrig if rechts_niedrig > rechts_hoch else rechts_hoch
            rechts = kontaktdistanz - 5.9
        space_range = rechts - links
        position = (links + rechts) / 2

        return {'links': links, 'rechts': rechts, 'range': space_range, 'position': position}

    def zeta_0mm(self):
        kontaktdistanz = self.m2_width / math.sin(self.angle / 180 * math.pi)
        cond1 = self.m1_width > 11

        if self.angle >= 90:
            cond2 = (max(self.links) < 14 - (math.tan(self.gehrung / 180 * math.pi) * 4 / math.sin(self.gehrung / 180 * math.pi)
                     - math.tan(self.gehrung / 180 * math.pi) * 4))
            cond3 = ((14 - (math.tan(self.gehrung / 180 * math.pi) * 4 / math.sin(self.gehrung / 180 * math.pi) -
                     math.tan(self.gehrung / 180 * math.pi) * 4)) < min(self.rechts))
        else:
            cond2 = (max(self.links) < kontaktdistanz - (14 - (math.tan(self.gehrung / 180 * math.pi) * 4 / math.sin(self.gehrung / 180 * math.pi)
                     - math.tan(self.gehrung / 180 * math.pi) * 4)))
            # Check
            cond3 = (kontaktdistanz - (14 - (math.tan(self.gehrung / 180 * math.pi) * 4 / math.sin(self.gehrung / 180 * math.pi) -
                     math.tan(self.gehrung / 180 * math.pi) * 4)) < min(self.rechts))

        return cond1 and cond2 and cond3

    def zeta_2mm(self):
        kontaktdistanz = self.m2_width / math.sin(self.angle / 180 * math.pi)
        cond1 = self.m1_width > 11

        if self.angle >= 90:
            cond2 = (max(self.links) < 14 - ((math.tan(self.gehrung / 180 * math.pi) * 4 / math.sin(self.gehrung / 180 * math.pi)
                     - math.tan(self.gehrung / 180 * math.pi) * 4) + 2 / math.cos(self.gehrung / 180 * math.pi)))
            cond3 = (14 - ((math.tan(self.gehrung / 180 * math.pi) * 4 / math.sin(self.gehrung / 180 * math.pi) -
                     math.tan(self.gehrung / 180 * math.pi) * 4) + 2 / math.cos(self.gehrung / 180 * math.pi)) < min(self.rechts))
        else:
            cond2 = (max(self.links) < kontaktdistanz - (14 - ((math.tan(self.gehrung / 180 * math.pi) * 4 / math.sin(self.gehrung / 180 * math.pi)
                     - math.tan(self.gehrung / 180 * math.pi) * 4) + 2 / math.cos(self.gehrung / 180 * math.pi))))
            cond3 = (kontaktdistanz - (14 - ((math.tan(self.gehrung / 180 * math.pi) * 4 / math.sin(self.gehrung / 180 * math.pi) -
                     math.tan(self.gehrung / 180 * math.pi) * 4) + 2 / math.cos(self.gehrung / 180 * math.pi))) < min(self.rechts))

        return cond1 and cond2 and cond3

    def zeta_4mm(self):
        return self.zeta_2mm()

    def check(self):
        schmalfl = self.calc_schmalfl()
        self.links.append(schmalfl['links'])
        self.rechts.append(schmalfl['rechts'])

        range_schmalfl = schmalfl['range']

        tmp_cnc = (max(self.links) + min(self.rechts)) / 2
        if tmp_cnc > range_schmalfl and tmp_cnc >= max(self.links) and tmp_cnc <= min(self.rechts):
            self.results['cnc']['possible'] = True
            self.results['cnc']['position'] = tmp_cnc

        self.results['zeta']['0mm']['possible'] = self.zeta_0mm()
        self.results['zeta']['2mm']['possible'] = self.zeta_2mm()
        self.results['zeta']['4mm']['possible'] = self.zeta_4mm()

        return self.results
