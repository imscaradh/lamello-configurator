from django.shortcuts import render
from django.http import HttpResponse
from .models import ConnectionType, Connector, init_db
from django.core import serializers
from .services import ConnectorService, PDFService

import json
import logging


def main(request):
    if len(ConnectionType.objects.all()) == 0:
        init_db()

    connectors = Connector.objects.all()
    connection_types = ConnectionType.objects.all()
    json_serialized = serializers.serialize('json', connection_types)

    return render(
        request,
        'configurator/index.html',
        {
            'connectors': connectors,
            'connection_types': connection_types,
            'connection_types_json': json_serialized
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
        pdf = PDFService(request.POST)
        return pdf.generatePDF
    else:
        return error_msg
