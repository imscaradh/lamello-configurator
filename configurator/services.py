import math


class BisecService:

    links = 5.9

    # Parameters for P-10
    p1 = 8.46
    p2 = 4.9
    p3 = 10
    p4 = 2.7

    m1_width = 0
    m2_width = 0
    angle = 90

    def __init__(self, m1_width, m2_width, angle):
        self.m1_width = m1_width
        self.m2_width = m2_width
        self.angle = angle

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
        space_range = rechts - BisecService.links
        position = (BisecService.links + rechts) / 2

        return {'rechts': rechts, 'range': space_range, 'position': position}

    def check(self):
        horizontal = self.calc_h()
        vertical = self.calc_v()

        range_h = horizontal['range']
        range_v = vertical['range']

        results = {}
        results['cnc'] = {}
        results['zeta'] = {}

        if range_h > 0 and range_v > 0:
            results['cnc']['possible'] = True
            rechts_h = horizontal['rechts']
            rechts_v = vertical['rechts']
            # FIXME: What is links?
            results['cnc']['position'] = (max(self.links, self.links) + min(rechts_v, rechts_h)) / 2
        else:
            results['cnc']['possible'] = False

        # TODO: Calculate
        if True:
            results['zeta']['0mm'] = True
            results['zeta']['2mm'] = True
            results['zeta']['4mm'] = True
        else:
            results['zeta']['0mm'] = False
            results['zeta']['2mm'] = False
            results['zeta']['4mm'] = False

        return results
