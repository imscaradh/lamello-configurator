from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from reportlab.lib.pagesizes import A4, portrait
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate

from .models import ConnectionType


def main(request):
    connection_types = ConnectionType.objects.all()
    # if len(connection_types) == 0:
    ConnectionType.objects.all().delete()
    c1 = ConnectionType(name="Stumb Edge", x1=40, y1=40, width1=40, height1=160, x2=80, y2=40, width2=160, height2=40)
    c1.save()
    c2 = ConnectionType(name="Bisectrix", x1=40, y1=80, width1=40, height1=160, x2=80, y2=40, width2=160, height2=40)
    c2.save()
    c3 = ConnectionType(name="Miter", x1=80, y1=80, width1=40, height1=160, x2=80, y2=40, width2=160, height2=40)
    c3.save()
    c4 = ConnectionType(name="T-Connection", x1=120, y1=40, width1=40, height1=160, x2=80, y2=80, width2=160,
                        height2=40)
    c4.save()
    c5 = ConnectionType(name="Septum", x1=40, y1=40, width1=40, height1=160, x2=80, y2=40, width2=160, height2=40)
    c5.save()
    # connection_types = ConnectionType.objects.all()
    json_serialized = serializers.serialize('json', connection_types)

    return render_to_response(
        'configurator/index.html',
        {
            'connection_types': connection_types,
            'connection_types_json': json_serialized,
        },
        context_instance=RequestContext(request)
    )


def pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=Lamello_Configurator.pdf'
    p = SimpleDocTemplate(response, pagesize=portrait(A4))

    m1 = 10
    m2 = 15
    angle = 90
    situation = "Winkelhalbierende"
    connector = "Verbinder"
    condesc = "Hier wird der Verbinder beschrieben."
    assdesc = "Beschrieb der Montage. Ob mit Handfraese oder CNC."
    data = "img-base64-string"
    style = getSampleStyleSheet()

    story = []

    story.append(Paragraph("Lamello", style['Title']))
    story.append(Paragraph("Situation: %s" % situation, style['Heading2']))
    story.append(Paragraph("Verbinder: %s" % connector, style['Heading2']))
    # story.append(img)
    story.append(Paragraph("Materialstärke  I: %d" % m1, style['BodyText']))
    story.append(Paragraph("Materialstärke II: %d" % m2, style['BodyText']))
    story.append(Paragraph("Winkel: %d" % angle, style['BodyText']))
    story.append(Paragraph("Beschreibung Verbinder:", style['Heading2']))
    story.append(Paragraph("%s:" % condesc, style['BodyText']))
    story.append(Paragraph("Beschreibung Montage:", style['Heading2']))
    story.append(Paragraph("%s:" % assdesc, style['BodyText']))

    p.build(story)

    return response
