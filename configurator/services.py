import math


class Service:
    m1_width = 0
    m2_width = 0
    angle = 90
    gehrung = 0
    links = []
    rechts = []
    results = {}

    def __init__(self, m1_width, m2_width, angle):
        self.m1_width = m1_width
        self.m2_width = m2_width
        self.angle = angle

        self.gehrung = abs(90 - angle / 2)

        self.results['cnc'] = {}
        self.results['cnc']['possible'] = False
        self.results['zeta'] = {}
        self.results['zeta']['0mm'] = False
        self.results['zeta']['2mm'] = False
        self.results['zeta']['4mm'] = False

    def zeta_0mm(self):
        raise NotImplementedError("Please Implement this method")

    def zeta_2mm(self):
        raise NotImplementedError("Please Implement this method")

    def zeta_4mm(self):
        raise NotImplementedError("Please Implement this method")

    def check(self):
        raise NotImplementedError("Please Implement this method")


class BisecService(Service):

    # Parameters for P-10
    p1 = 8.46
    p2 = 4.9
    p3 = 10
    p4 = 2.7

    def __init__(self, m1_width, m2_width, angle):
        Service.__init__(self, m1_width, m2_width, angle)
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
        rechts_niedrig = (kontaktdistanz - (1 / math.cos(schnittwinkel / 180 * math.pi) + self.p1)
                          / math.tan(schnittwinkel / 180 * math.pi) - self.p2)
        rechts_hoch = (kontaktdistanz - (1 / math.cos(schnittwinkel / 180 * math.pi) + self.p3)
                       / math.tan(schnittwinkel / 180 * math.pi) - self.p4)

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

        self.results['zeta']['0mm'] = self.zeta_0mm()
        self.results['zeta']['2mm'] = self.zeta_2mm()
        self.results['zeta']['4mm'] = self.zeta_4mm()

        return self.results
