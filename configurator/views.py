import base64
import io
import os.path

from django.shortcuts import render
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from .models import ConnectionType, Connector
from django.core import serializers
from reportlab.lib.pagesizes import portrait
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Image, Table, TableStyle, ImageAndFlowables
from .services import ConnectorService, PDFService

import json
import logging


def main(request, calc_result=None):
    connection_types = ConnectionType.objects.all()
    # uncommented for debugging
    # if len(connection_types) == 0:
    ConnectionType.objects.all().delete()
    c1 = ConnectionType(name="Stumb Edge", x1=40, y1=40, width1=40, height1=200, x2=80, y2=200, width2=200, height2=40)
    c1.save()
    c2 = ConnectionType(name="Bisectrix", x1=40, y1=40, width1=40, height1=160, x2=80, y2=200, width2=200, height2=40)
    c2.save()
    c3 = ConnectionType(name="T-Connection", x1=140, y1=80, width1=40, height1=160, x2=80, y2=40, width2=160,
                        height2=40)
    c3.save()
    c4 = ConnectionType(name="Miter", x1=160, y1=40, width1=40, height1=200, x2=80, y2=170, width2=100, height2=40,
                        x3=180, y3=170, width3=100, height3=40)
    c4.save()
    connection_types = ConnectionType.objects.all()
    json_serialized = serializers.serialize('json', connection_types)

    Connector.objects.all().delete()
    p1 = Connector(name="P10", p1=8.46, p2=4.9, p3=10, p4=2.7, min_m1=11,
                   info="Clamex P-10 ist eine Ergänzung zum P-System Verbindungssystem für dünnere Materialstärken ab 13mm")
    p1.save()
    p2 = Connector(name="P14", p1=12.46, p2=4.9, p3=14, p4=2.7, min_m1=15,
                   info="Clamex P-14, der Nachfolger des erfolgreichen Clamex P-15, ist ein zerlegbarer Verbindungs \
                            beschlag mit sekundenschneller formschlüssiger P-System Verankerung")
    p2.save()
    p3 = Connector(name="P1014", p1=12.46, p2=4.9, p3=14, p4=2.7, min_m1=15,
                   info="Clamex P Medius ist der Mittelwandverbinder passend zum Clamex P-14 Verbinder für Materialstärken ab 16mm")
    p3.save()

    return render(
        request,
        'configurator/index.html',
        {
            'connection_types': connection_types,
            'connection_types_json': json_serialized,
            'calc_result': calc_result,
        }
    )


def calc(request):
    error_msg = HttpResponse(status=500)

    if request.method == 'POST' and request.POST is not None:

        angle = request.POST['angle']
        m1_width = request.POST['m1']
        m2_width = request.POST['m2']
        unit = request.POST['unit']

        connection_type = request.POST['connection_type']

        if None in (unit, m1_width, m2_width, angle, connection_type):
            return error_msg

        try:
            angle = float(angle)
            m1_width = float(m1_width)
            m2_width = float(m2_width)
            if unit == "in":
                m1_width = m1_width * 25.4
                m2_width = m2_width * 25.4

            calc_results = {}
            service = ConnectorService.factory(connection_type, m1_width, m2_width, angle)

            for connector in Connector.connections:
                service.set_connector(connector)
                tmp = service.check()
                calc_results[connector] = tmp

            return HttpResponse(
                json.dumps(calc_results),
                content_type="application/json"
            )
        except Exception as e:
            logging.exception(e)
            return error_msg
    else:
        return error_msg


def pdf(request):
    error_msg = HttpResponse(status=500)
    if request.method == 'POST' and request.POST is not None:
        m1 = request.POST['m1']
        m2 = request.POST['m2']
        # unit = request.POST['unit']
        angle = request.POST['angle']
        situation = request.POST['situation']
        data = request.POST['dataURL']
        connector = request.POST['connector']
        cncPossible = request.POST['cncPossible']
        cncPosition = request.POST['cncPosition']
        zeta0 = request.POST['zeta0']
        zeta2 = request.POST['zeta2']
        zeta4 = request.POST['zeta4']
        zeta0a = request.POST['zeta0a']
        zeta0b = request.POST['zeta0b']
        zeta2a = request.POST['zeta2a']
        zeta2b = request.POST['zeta2b']
        zeta4a = request.POST['zeta4a']
        zeta4b = request.POST['zeta4b']

        pdf = PDFService(m1, m2, angle, situation, data, connector, cncPossible, cncPosition, zeta0, zeta2, zeta4,
                         zeta0a, zeta0b, zeta2a, zeta2b, zeta4a, zeta4b)

        return pdf.generatePDF
    else:
        return error_msg
