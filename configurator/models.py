from django.db import models


class ConnectionType(models.Model):
    name = models.CharField(max_length=30)
    width1 = models.IntegerField(default=0)
    height1 = models.IntegerField(default=0)
    x1 = models.IntegerField(default=0)
    y1 = models.IntegerField(default=0)
    width2 = models.IntegerField(default=0)
    height2 = models.IntegerField(default=0)
    x2 = models.IntegerField(default=0)
    y2 = models.IntegerField(default=0)
    width3 = models.IntegerField(default=0)
    height3 = models.IntegerField(default=0)
    x3 = models.IntegerField(default=0)
    y3 = models.IntegerField(default=0)


class Connector(models.Model):
    connections = ["P10", "P14", "P1014"]

    name = models.CharField(max_length=30)
    p1 = models.DecimalField(default=0, max_digits=19, decimal_places=3)
    p2 = models.DecimalField(default=0, max_digits=19, decimal_places=3)
    p3 = models.DecimalField(default=0, max_digits=19, decimal_places=3)
    p4 = models.DecimalField(default=0, max_digits=19, decimal_places=3)
    min_m1 = models.DecimalField(default=0, max_digits=19, decimal_places=3)
    info = models.CharField(max_length=512, default="")
