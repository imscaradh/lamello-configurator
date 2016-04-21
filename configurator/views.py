from django.shortcuts import render_to_response
from django.template import RequestContext
from .models import ConnectionType
from django.core import serializers


def main(request):
    connection_types = ConnectionType.objects.all()
    # if len(connection_types) == 0:
    ConnectionType.objects.all().delete()
    c1 = ConnectionType(name="Stumb Edge", x1=40, y1=40, width1=40, height1=160, x2=80, y2=40, width2=160, height2=40)
    c1.save()
    c2 = ConnectionType(name="Bisectrix", x1=40, y1=40, width1=40, height1=160, x2=80, y2=40, width2=160, height2=40)
    c2.save()
    c3 = ConnectionType(name="Miter", x1=40, y1=40, width1=40, height1=160, x2=80, y2=40, width2=160, height2=40)
    c3.save()
    c4 = ConnectionType(name="T-Connection", x1=40, y1=40, width1=40, height1=160, x2=80, y2=40, width2=160, height2=40)
    c4.save()
    c5 = ConnectionType(name="Septum", x1=40, y1=40, width1=40, height1=160, x2=80, y2=40, width2=160, height2=40)
    c5.save()
    connection_types = ConnectionType.objects.all()
    json_serialized = serializers.serialize('json', connection_types)

    return render_to_response(
        'configurator/index.html',
        {
            'connection_types': connection_types,
            'connection_types_json': json_serialized,
        },
        context_instance=RequestContext(request)
    )
