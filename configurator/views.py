from django.shortcuts import render
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from django.core import serializers
from reportlab.lib.pagesizes import portrait
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate
from .models import ConnectionType
from .services import BisecService
import json


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
    if request.method == 'POST':
        m1_width = request.POST['m1']
        m2_width = request.POST['m2']
        angle = request.POST['angle']

        m1_width = float(m1_width)
        m2_width = float(m2_width)
        angle = float(angle)

        bisec = BisecService(m1_width, m2_width, angle)
        calc_result = bisec.check()

        return HttpResponse(
            json.dumps(calc_result),
            content_type="application/json"
        )
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )


def pdf(request):
    if request.method == 'POST':
        m1 = request.POST['m1']
        m2 = request.POST['m2']
        angle = request.POST['angle']
        situation = request.POST['connection_type']

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=Lamello_Configurator.pdf'
        p = SimpleDocTemplate(response, pagesize=portrait(A4))

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
        story.append(Paragraph("Materialstärke  I: %s" % m1, style['BodyText']))
        story.append(Paragraph("Materialstärke II: %s" % m2, style['BodyText']))
        story.append(Paragraph("Winkel: %s°" % angle, style['BodyText']))
        story.append(Paragraph("Beschreibung Verbinder:", style['Heading2']))
        story.append(Paragraph("%s:" % condesc, style['BodyText']))
        story.append(Paragraph("Beschreibung Montage:", style['Heading2']))
        story.append(Paragraph("%s:" % assdesc, style['BodyText']))

        p.build(story)

        return response
    else:
        return HttpResponse(

        )
