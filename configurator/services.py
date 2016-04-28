import math


class BisecService:

    links = 5.9

    @staticmethod
    def calc_h(m1_width, m2_width, angle):
        kontaktdistanz = math.sqrt(((m2_width + m1_width / math.cos(angle / 180 * math.pi)) / math.tan(angle / 180 * math.pi)) ** 2 + m2_width ** 2)

        schnittwinkel = 90 - math.degrees(math.acos(m2_width / kontaktdistanz))
        rechts_niedrig = kontaktdistanz - (1 / math.cos(schnittwinkel / 180 * math.pi) + 8.46) / math.tan(schnittwinkel / 180 * math.pi) - 4.9
        rechts_hoch = kontaktdistanz - (1 / math.cos(schnittwinkel / 180 * math.pi) + 10) / math.tan(schnittwinkel / 180 * math.pi) - 2.7

        rechts = rechts_niedrig if rechts_niedrig < rechts_hoch else rechts_hoch
        space_range = rechts - BisecService.links
        position = (BisecService.links + rechts) / 2

        return position

    def calc_v(self, m1_width, m2_width, angle):
        return
