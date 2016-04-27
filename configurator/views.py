from django.shortcuts import render
from .models import ConnectionType
from django.core import serializers
from .services import calc_bisec


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
    m1_width = request.POST['m1']
    m2_width = request.POST['m2']
    angle = request.POST['angle']

    m1_width = float(m1_width)
    m2_width = float(m2_width)
    angle = float(angle)

    calc_result = calc_bisec(m1_width, m2_width, angle)

    # Maybe a subrendering cloud be performed
    return main(request, {'conn_cnc': calc_result})
