from django.contrib import admin
from configurator.models import ConnectionType, Connector


admin.site.register(ConnectionType)
admin.site.register(Connector)
