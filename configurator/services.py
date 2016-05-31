import base64
import io
import math
import os

from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import portrait, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, SimpleDocTemplate, TableStyle, Table
from reportlab.platypus.para import Paragraph
from django.utils.translation import ugettext_lazy as _
from django.utils import translation

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
        cond2 = (
            self.links_max < 14 - (math.tan(self.gehrung / 180 * math.pi) * 4 / math.sin(self.gehrung / 180 * math.pi)
                                   - math.tan(self.gehrung / 180 * math.pi) * 4))
        cond3 = ((14 - (math.tan(self.gehrung / 180 * math.pi) * 4 / math.sin(self.gehrung / 180 * math.pi) -
                        math.tan(self.gehrung / 180 * math.pi) * 4)) < min(self.rechts))

        return cond1 and cond2 and cond3

    def zeta_2mm(self):
        cond1 = (self.m1_width == self.m2_width)
        cond2 = (
            self.links_max < 14 - ((math.tan(self.gehrung / 180 * math.pi) * 4 / math.sin(self.gehrung / 180 * math.pi)
                                    - math.tan(self.gehrung / 180 * math.pi) * 4) + 2 / math.cos(
                self.gehrung / 180 * math.pi)))
        cond3 = (14 - ((math.tan(self.gehrung / 180 * math.pi) * 4 / math.sin(self.gehrung / 180 * math.pi) -
                        math.tan(self.gehrung / 180 * math.pi) * 4) + 2 / math.cos(self.gehrung / 180 * math.pi)) < min(
            self.rechts))

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
                                        math.sin(self.stumb / 180 * math.pi) - math.tan(
            self.stumb / 180 * math.pi) * 4)))

        cond2 = (max(self.links) < val2)
        cond3 = (val1 < min(self.rechts))

        return {'possible': cond1 and cond2 and cond3, 'val': [val1, val2]}

    def zeta_2mm(self):
        kontaktdistanz = self.m2_width / math.sin(self.angle / 180 * math.pi)
        cond1 = self.m1_width > 11

        val1 = (14 - ((math.tan(self.stumb / 180 * math.pi) * 4 /
                       math.sin(self.stumb / 180 * math.pi) - math.tan(self.stumb / 180 * math.pi) * 4) + 2 / math.cos(
            self.stumb / 180 * math.pi)))
        val2 = (kontaktdistanz - (14 - ((math.tan(self.stumb / 180 * math.pi) * 4 /
                                         math.sin(self.stumb / 180 * math.pi) - math.tan(
            self.stumb / 180 * math.pi) * 4) + 2 / math.cos(self.stumb / 180 * math.pi))))

        cond2 = (max(self.links) < val2)
        cond3 = (val1 < min(self.rechts))

        return {'possible': cond1 and cond2 and cond3, 'val': [val1, val2]}

    def zeta_4mm(self):
        kontaktdistanz = self.m2_width / math.sin(self.angle / 180 * math.pi)
        cond1 = self.m1_width > 11

        val1 = (14 - ((math.tan(self.stumb / 180 * math.pi) * 4 /
                       math.sin(self.stumb / 180 * math.pi) - math.tan(self.stumb / 180 * math.pi) * 4) + 4 / math.cos(
            self.stumb / 180 * math.pi)))
        val2 = (kontaktdistanz - (14 - ((math.tan(self.stumb / 180 * math.pi) * 4 /
                                         math.sin(self.stumb / 180 * math.pi) - math.tan(
            self.stumb / 180 * math.pi) * 4) + 4 / math.cos(self.stumb / 180 * math.pi))))

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
        if (range_schmalfl > 0 and tmp_cnc >= max(self.links) and tmp_cnc <= min(self.rechts)
                and self.m1_width >= float(self.connector.min_m1)):
            self.results['cnc']['possible'] = True
            self.results['cnc']['position'] = tmp_cnc

        self.results['zeta']['0mm'] = self.zeta_0mm()
        self.results['zeta']['2mm'] = self.zeta_2mm()
        self.results['zeta']['4mm'] = self.zeta_4mm()

        return self.results


class TConnectionService(ConnectorService):

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

        val1 = (14 - (math.tan(self.stumb / 180 * math.pi) * 4 /
                      math.sin(self.stumb / 180 * math.pi) - math.tan(self.stumb / 180 * math.pi) * 4))
        val2 = (kontaktdistanz - (14 - (math.tan(self.stumb / 180 * math.pi) * 4 /
                                        math.sin(self.stumb / 180 * math.pi) - math.tan(
            self.stumb / 180 * math.pi) * 4)))

        cond2 = (max(self.links) < val2)
        cond3 = (val1 < min(self.rechts))

        return {'possible': cond1 and cond2 and cond3, 'val': [val1, val2]}

    def zeta_2mm(self):
        kontaktdistanz = self.m2_width / math.sin(self.angle / 180 * math.pi)
        cond1 = self.m1_width > 11

        val1 = (14 - ((math.tan(self.stumb / 180 * math.pi) * 4 /
                       math.sin(self.stumb / 180 * math.pi) - math.tan(self.stumb / 180 * math.pi) * 4) + 2 / math.cos(
            self.stumb / 180 * math.pi)))
        val2 = (kontaktdistanz - (14 - ((math.tan(self.stumb / 180 * math.pi) * 4 /
                                         math.sin(self.stumb / 180 * math.pi) - math.tan(
            self.stumb / 180 * math.pi) * 4) + 2 / math.cos(self.stumb / 180 * math.pi))))

        cond2 = (max(self.links) < val2)
        cond3 = (val1 < min(self.rechts))

        return {'possible': cond1 and cond2 and cond3, 'val': [val1, val2]}

    def zeta_4mm(self):
        kontaktdistanz = self.m2_width / math.sin(self.angle / 180 * math.pi)
        cond1 = self.m1_width > 11

        val1 = (14 - ((math.tan(self.stumb / 180 * math.pi) * 4 /
                       math.sin(self.stumb / 180 * math.pi) - math.tan(self.stumb / 180 * math.pi) * 4) + 4 / math.cos(
            self.stumb / 180 * math.pi)))
        val2 = (kontaktdistanz - (14 - ((math.tan(self.stumb / 180 * math.pi) * 4 /
                                         math.sin(self.stumb / 180 * math.pi) - math.tan(
            self.stumb / 180 * math.pi) * 4) + 4 / math.cos(self.stumb / 180 * math.pi))))

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

        tmp_cnc = (max(self.links) + min(self.rechts)) / 2
        if schmalfl['range'] > 0 and fl['range'] >= 0 and self.m1_width >= float(self.connector.min_m1):
            self.results['cnc']['possible'] = True
            self.results['cnc']['position'] = tmp_cnc

        self.results['zeta']['0mm'] = self.zeta_0mm()
        self.results['zeta']['2mm'] = self.zeta_2mm()
        self.results['zeta']['4mm'] = self.zeta_4mm()

        return self.results


class MiterService(ConnectorService):
    t_service = None

    def __init__(self, m1_width, m2_width, angle):
        ConnectorService.__init__(self, m1_width, m2_width, angle)

    def calc_schmalfl(self):
        kontaktdistanz = self.m2_width / math.sin(self.angle / 180 * math.pi)

        m_range = abs(kontaktdistanz - 2 * self.links_max)
        links = self.links_max
        rechts = self.links_max + m_range / 2 - float(self.connector.p2)

        return {'links': links, 'rechts': rechts, 'range': m_range}

    def zeta_0mm(self):
        rechts_tconn = self.t_service_schmalfl['rechts']

        val = (14 - (math.tan(self.stumb / 180 * math.pi) * 4 / math.sin(self.stumb / 180 * math.pi)
                     - math.tan(self.stumb / 180 * math.pi) * 4))

        tmp1 = self.m1_width >= 21
        tmp2 = (5.9 < val)
        tmp3 = (val < rechts_tconn)
        tmp4 = self.m1_width >= 11
        tmp5 = True
        tmp6 = tmp2
        tmp7 = (val < self.m_rechts)

        possible = (tmp1 and tmp2 and tmp3) or (tmp4 and tmp5 and tmp6 and tmp7)
        return {'possible': possible, 'val': self.t_service_result['zeta']['0mm']['val']}

    def zeta_2mm(self):
        rechts_tconn = self.t_service_schmalfl['rechts']

        val = (14 - ((math.tan(self.stumb / 180 * math.pi) * 4 / math.sin(self.stumb / 180 * math.pi)
                      - math.tan(self.stumb / 180 * math.pi) * 4) + 2 / math.cos(self.stumb / 180 * math.pi)))

        tmp1 = self.m1_width >= 21
        tmp2 = (5.9 < val)
        tmp3 = (val < rechts_tconn)
        tmp4 = self.m1_width >= 11
        tmp5 = True
        tmp6 = tmp2
        tmp7 = (val < self.m_rechts)

        possible = (tmp1 and tmp2 and tmp3) or (tmp4 and tmp5 and tmp6 and tmp7)
        return {'possible': possible, 'val': self.t_service_result['zeta']['2mm']['val']}

    def zeta_4mm(self):
        rechts_tconn = self.t_service_schmalfl['rechts']

        val = (14 - ((math.tan(self.stumb / 180 * math.pi) * 4 / math.sin(self.stumb / 180 * math.pi)
                      - math.tan(self.stumb / 180 * math.pi) * 4) + 4 / math.cos(self.stumb / 180 * math.pi)))

        tmp1 = self.m1_width >= 21
        tmp2 = (5.9 < val)
        tmp3 = (val < rechts_tconn)
        tmp4 = self.m1_width >= 11
        tmp5 = True
        tmp6 = tmp2
        tmp7 = (val < self.m_rechts)

        possible = (tmp1 and tmp2 and tmp3) or (tmp4 and tmp5 and tmp6 and tmp7)
        return {'possible': possible, 'val': self.t_service_result['zeta']['4mm']['val']}

    def check(self):
        t_service = TConnectionService(self.m1_width, self.m2_width, self.angle)
        t_service.set_connector(self.connector.name)
        self.t_service_schmalfl = t_service.calc_schmalfl()
        self.t_service_result = t_service.check()

        schmalfl = self.calc_schmalfl()

        m_range = schmalfl['range']
        m_links = schmalfl['links']
        self.m_rechts = schmalfl['rechts']
        cnc_tconn = self.t_service_result['cnc']

        # TOOD: Possible simplification?
        if (m_range >= 11 and cnc_tconn['possible'] and self.m1_width >= 9.8) or (self.angle >= 21 and cnc_tconn['possible']):
            self.results['cnc']['possible'] = True

            if self.m1_width >= 21:
                self.results['cnc']['position'] = cnc_tconn['position']
            elif (m_links + self.m_rechts) / 2 < cnc_tconn['position']:
                self.results['cnc']['position'] = (m_links + self.m_rechts) / 2
            else:
                self.results['cnc']['position'] = cnc_tconn['position']

        self.results['zeta']['0mm'] = self.zeta_0mm()
        self.results['zeta']['2mm'] = self.zeta_2mm()
        self.results['zeta']['4mm'] = self.zeta_4mm()

        return self.results


class PDFService:

    def __init__(self, data):
        self.m1 = data['m1']
        self.m2 = data['m2']
        self.angle = data['angle']
        self.situation = data['situation']
        self.imgData = data['dataURL']
        self.connector = data['connector']
        self.cncPossible = data['cncPossible']
        self.cncPosition = data['cncPosition']
        self.zeta0 = data['zeta0']
        self.zeta2 = data['zeta2']
        self.zeta4 = data['zeta4']
        self.zeta0a = data['zeta0a']
        self.zeta0b = data['zeta0b']
        self.zeta2a = data['zeta2a']
        self.zeta2b = data['zeta2b']
        self.zeta4a = data['zeta4a']
        self.zeta4b = data['zeta4b']

    @property
    def generatePDF(self):
        """The code below generats the PDF. Reportlab is use for the generation. The datas comes from the ajax-call.

        The PDF contains three tables:
        - titletable: contains Title and Logo
        - situationtable: contains the situationimage and the two materialthikness and the angle
        - table: contains the zetaP2 and CNC Position for the installation

        All parts of the PDF append in a story and will build in the end.
        """
        con = self.connector.replace("-", "")
        allconnectorinfos = Connector.objects.all()
        connectorinfo = allconnectorinfos.filter(name="%s" % con).first()
        if translation.get_language() == 'de':
            info = connectorinfo.info_de
        else:
            info = connectorinfo.info_en

        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/img/logo.jpg')
        logo = Image(logo_path, width=3 * cm, height=3 * cm, hAlign='LEFT', kind='proportional')

        im = Image(io.BytesIO(base64.b64decode(self.imgData.split(',')[1])), hAlign='LEFT', width=13 * cm,
                   height=13 * cm,
                   kind='proportional')

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = ' filename=Lamello_Configurator.pdf'
        p = SimpleDocTemplate(response, pagesize=portrait(A4))

        style = getSampleStyleSheet()

        titeltabledata = [(Paragraph(_('Configurator'), style['Heading1']), logo)]

        titeltablestyle = TableStyle([('ALIGN', (0, 0), (0, 0), 'LEFT'),
                                      ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
                                      ('ALIGN', (1, 0), (1, 0), 'RIGHT')])

        titletable = Table(titeltabledata, hAlign='LEFT', colWidths=8 * cm)
        titletable.setStyle(titeltablestyle)

        mt1 = Paragraph(_('Material thickness  I: %smm') % self.m1, style['BodyText'])
        mt2 = Paragraph(_('Material thickness II: %smm') % self.m2, style['BodyText'])
        ang = Paragraph(_('Angle: %s°') % self.angle, style['BodyText'])

        situationtabledata = [([mt1, mt2, ang], im)]

        situationtablestyle = TableStyle([('ALIGN', (0, 0), (0, 0), 'LEFT'),
                                          ('ALIGN', (-1, -1), (-1, -1), 'LEFT'),
                                          ('VALIGN', (0, 0), (0, 0), 'MIDDLE')])

        situationtable = Table(situationtabledata, hAlign='LEFT', colWidths=7 * cm)
        situationtable.setStyle(situationtablestyle)

        tabledata = [(Paragraph('CNC:', style['Heading4']), _('Possible'), 'a', 'b'),
                     ('', '%s' % self.cncPossible, '%smm' % self.cncPosition, '0mm'),
                     '',
                     (Paragraph('Zeta P2:', style['Heading4']), _('Possible'), 'a', 'b'),
                     (_('0mm board'), '%s' % self.zeta0, '%smm' % self.zeta0a, '%smm' % self.zeta0b),
                     (_('2mm board'), '%s' % self.zeta2, '%smm' % self.zeta2a, '%smm' % self.zeta2b),
                     (_('4mm board'), '%s' % self.zeta4, '%smm' % self.zeta4a, '%smm' % self.zeta4b)]

        tablestyle = TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                 ('ALIGN', (0, 0), (-1, 1), 'LEFT'),
                                 ('BOX', (0, 0), (3, 1), 0.25, colors.black),
                                 ('BOX', (0, 3), (-1, -1), 0.25, colors.black),
                                 ('INNERGRID', (0, 0), (3, 1), 0.25, colors.black),
                                 ('INNERGRID', (0, 3), (-1, -1), 0.25, colors.black)
                                 ])

        table = Table(tabledata, colWidths=(5 * cm, 3 * cm, 3 * cm, 3 * cm), hAlign='LEFT')
        table.setStyle(tablestyle)

        story = []

        story.append(titletable)
        story.append(Paragraph(_('Situation: %s') % self.situation, style['Heading2']))
        story.append(Paragraph(_('Connector: %s') % self.connector, style['Heading2']))
        story.append(situationtable)
        story.append(Paragraph(_('Connector description'), style['Heading2']))
        story.append(Paragraph("%s" % info, style['BodyText']))
        story.append(Paragraph(_('Installation'), style['Heading2']))
        story.append(table)

        p.build(story)

        return response
