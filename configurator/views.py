from django.shortcuts import render
from django.http import HttpResponse
from reportlab.pdfgen import canvas
<<<<<<< 95e77885346bc0d143245b58baeaa8214d591b76
=======
from reportlab.lib.pagesizes import A4

>>>>>>> PDF Prototype
from .models import ConnectionType
from django.core import serializers
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
    c3 = ConnectionType(name="T-Connection", x1=130, y1=80, width1=40, height1=160, x2=80, y2=40, width2=160, height2=40)
    c3.save()
    c4 = ConnectionType(name="Miter", x1=120, y1=40, width1=40, height1=160, x2=80, y2=80, width2=160, height2=40)
    c4.save()
    c5 = ConnectionType(name="Septum", x1=40, y1=40, width1=40, height1=160, x2=80, y2=40, width2=160, height2=40)
    c5.save()
    connection_types = ConnectionType.objects.all()
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
    m1 = 10
    m2 = 15
    angle = 90
    situation = "Winkelhalbierende"
    conDesc = "Hier wird der Verbinder beschrieben."
    assDesc = "Beschrieb der Montage. Ob mit Handfraese oder CNC."

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="somefilename.pdf"'

    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.setFont("Courier", 20)
    p.drawString(100, 750, "Lamello")
    p.line(100, 748, 525, 748)

    p.setFont("Courier", 15)
    p.drawString(100, 725, "Verbinder: xyz")

    p.drawString(100, 700, "Situation: %s" % situation)

    p.rect(100, 480, 250, 200)
    p.setFont("Courier", 12)
    p.drawString(370, 670, "Materialstärke I:  %d mm" % m1)
    p.drawString(370, 650, "Materialstärke II: %d mm" % m2)
    p.drawString(370, 630, "Winkel:            %d°" % angle)

    p.setFont("Courier", 15)
    p.drawString(100, 450, "Beschreibung Verbinder:")
    p.setFont("Courier", 12)
    p.drawString(100, 430, "%s" % conDesc)

    p.setFont("Courier", 15)
    p.drawString(100, 300, "Beschreibung Montage:")
    p.setFont("Courier", 12)
    p.drawString(100, 280, "%s" % assDesc)

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    return response
