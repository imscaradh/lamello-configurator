from django.contrib import admin
from configurator.models import ConnectionType, Connector


# This allows to edit the model data
admin.site.register(ConnectionType)
admin.site.register(Connector)
