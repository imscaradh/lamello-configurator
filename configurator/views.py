from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from reportlab.pdfgen import canvas
from reportlab.lib import fonts

from .models import ConnectionType
from django.core import serializers


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

    p.drawString(100, 700, "Situation:")

    p.rect(100, 480, 300, 200)

    p.drawString(100, 450, "Beschreibung Verbinder:")

    p.drawString(100, 300, "Beschreibung Montage:")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    return response
