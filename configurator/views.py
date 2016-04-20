from django.shortcuts import render_to_response
from django.template import RequestContext
from .models import ConnectionType


def main(request):
    connection_types = ConnectionType.objects.all()
    if len(connection_types) == 0:
        c1 = ConnectionType(name="Stumb Edge")
        c1.save()
        c2 = ConnectionType(name="BisecSeptumtrix")
        c2.save()
        c3 = ConnectionType(name="Miter")
        c3.save()
        c4 = ConnectionType(name="T-Connection")
        c4.save()
        c5 = ConnectionType(name="Septum")
        c5.save()
        connection_types = ConnectionType.objects.all()

    return render_to_response(
        'configurator/index.html',
        {'connection_types': connection_types},
        context_instance=RequestContext(request)
    )
