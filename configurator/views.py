from django.shortcuts import render
from django.http import HttpResponse
from .models import ConnectionType, Connector
from django.core import serializers
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
    c3 = ConnectionType(name="T-Connection", x1=130, y1=80, width1=40, height1=160, x2=80, y2=40, width2=160, height2=40)
    c3.save()
    c4 = ConnectionType(name="Miter", x1=120, y1=40, width1=40, height1=160, x2=80, y2=80, width2=160, height2=40)
    c4.save()
    connection_types = ConnectionType.objects.all()
    json_serialized = serializers.serialize('json', connection_types)

    Connector.objects.all().delete()
    p1 = Connector(name="P10", p1=8.46, p2=4.9, p3=10, p4=2.7)
    p1.save()
    p2 = Connector(name="P14", p1=12.46, p2=4.9, p3=14, p4=2.7)
    p2.save()
    p3 = Connector(name="P1014", p1=12.46, p2=4.9, p3=14, p4=2.7)
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
