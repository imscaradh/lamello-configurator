import base64
import io
from django.shortcuts import render
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from .models import ConnectionType, Connector, Info
from django.core import serializers
from reportlab.lib.pagesizes import portrait
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Image
from .services import ConnectorService
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
    c3 = ConnectionType(name="T-Connection", x1=130, y1=80, width1=40, height1=160, x2=80, y2=40, width2=160,
                        height2=40)
    c3.save()
    c4 = ConnectionType(name="Miter", x1=120, y1=40, width1=40, height1=160, x2=80, y2=80, width2=160, height2=40)
    c4.save()
    c5 = ConnectionType(name="Septum", x1=40, y1=40, width1=40, height1=160, x2=80, y2=40, width2=160, height2=40)
    c5.save()
    # connection_types = ConnectionType.objects.all()
    json_serialized = serializers.serialize('json', connection_types)

    Connector.objects.all().delete()
    p1 = Connector(name="P10", p1=8.46, p2=4.9, p3=10, p4=2.7)
    p1.save()
    p2 = Connector(name="P14", p1=12.46, p2=4.9, p3=14, p4=2.7)
    p2.save()
    p3 = Connector(name="P1014", p1=12.46, p2=4.9, p3=14, p4=2.7)
    p3.save()

    Info.objects.all().delete()
    i1 = Info(name="P-10", info="Clamex P-10 ist eine Ergänzung zum P-System Verbindungssystem für dünnere "
                                         "Materialstärken ab 13mm")
    i1.save()
    i2 = Info(name="P-14", info="Clamex P-14, der Nachfolger des erfolgreichen Clamex P-15, ist ein "
                                         "zerlegbarer Verbindungsbeschlag mit sekundenschneller formschlüssiger "
                                         "P-System Verankerung")
    i2.save()
    i3 = Info(name="P-1014", info="Clamex P Medius ist der Mittelwandverbinder passend zum Clamex P-14 "
                                           "Verbinder für Materialstärken ab 16mm")
    i3.save()

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
        m1_width = request.POST['m1']
        m2_width = request.POST['m2']
        angle = request.POST['angle']
        connection_type = request.POST['connection_type']

        if None in (m1_width, m2_width, angle, connection_type):
            return error_msg

        try:
            m1_width = float(m1_width)
            m2_width = float(m2_width)
            angle = float(angle)

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
    if request.method == 'POST':
        m1 = request.POST['m1']
        m2 = request.POST['m2']
        angle = request.POST['angle']
        situation = request.POST['situation']
        data = request.POST['dataURL']
        connector = request.POST['connector']
        allconnectorinfos = Info.objects.all()
        connectorinfo = allconnectorinfos.filter(name="%s" % connector).first()
        info = connectorinfo.info
        cncPossible = request.POST['cncPossible']
        cncPosition = request.POST['cncPosition']
        zeta0 = request.POST['zeta0']
        zeta2 = request.POST['zeta2']
        zeta4 = request.POST['zeta4']

        im = Image(io.BytesIO(base64.b64decode(data.split(',')[1])))

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = ' filename=Lamello_Configurator.pdf'
        p = SimpleDocTemplate(response, pagesize=portrait(A4))

        style = getSampleStyleSheet()

        story = []

        story.append(Paragraph("Lamello", style['Title']))
        story.append(Paragraph("Situation: %s" % situation, style['Heading2']))
        story.append(Paragraph("Verbinder: %s" % connector, style['Heading2']))
        story.append(im)
        story.append(Paragraph("Materialstärke  I: %s" % m1, style['BodyText']))
        story.append(Paragraph("Materialstärke II: %s" % m2, style['BodyText']))
        story.append(Paragraph("Winkel: %s°" % angle, style['BodyText']))
        story.append(Paragraph("Beschreibung Verbinder:", style['Heading2']))
        story.append(Paragraph("%s:" % info, style['BodyText']))
        story.append(Paragraph("Beschreibung Montage:", style['Heading2']))
        story.append(Paragraph("CNC:", style['Heading3']))
        story.append(Paragraph("%s:" % cncPossible, style['BodyText']))
        story.append(Paragraph("%s:" % cncPosition, style['BodyText']))
        story.append(Paragraph("Zeta:", style['Heading3']))
        story.append(Paragraph("0mm: %s" % zeta0, style['BodyText']))
        story.append(Paragraph("2mm: %s" % zeta2, style['BodyText']))
        story.append(Paragraph("4mm: %s" % zeta4, style['BodyText']))

        p.build(story)

        return response
    else:
        return HttpResponse()

