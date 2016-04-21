from django.db import models


class ConnectionType(models.Model):
    name = models.CharField(max_length=30)
    width1 = models.IntegerField()
    height1 = models.IntegerField()
    x1 = models.IntegerField()
    y1 = models.IntegerField()
    width2 = models.IntegerField()
    height2 = models.IntegerField()
    x2 = models.IntegerField()
    y2 = models.IntegerField()
