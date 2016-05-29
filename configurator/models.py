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


def init_db():
    ConnectionType.objects.all().delete()
    c1 = ConnectionType(name="Stumb Edge", x1=40, y1=40, width1=40, height1=200, x2=80, y2=200, width2=200, height2=40)
    c1.save()
    c2 = ConnectionType(name="Bisectrix", x1=40, y1=40, width1=40, height1=160, x2=80, y2=200, width2=200, height2=40)
    c2.save()
    c3 = ConnectionType(name="T-Connection", x1=140, y1=80, width1=40, height1=160, x2=80, y2=40, width2=160,
                        height2=40)
    c3.save()
    c4 = ConnectionType(name="Miter", x1=240, y1=40, width1=40, height1=230, x2=100, y2=150, width2=165, height2=40,
                        x3=255, y3=150, width3=165, height3=40)
    c4.save()
    connection_types = ConnectionType.objects.all()

    Connector.objects.all().delete()
    p1 = Connector(name="P10", p1=8.46, p2=4.9, p3=10, p4=2.7, min_m1=11,
                   info="Clamex P-10 ist eine Ergänzung zum P-System Verbindungssystem für dünnere Materialstärken ab 13mm")
    p1.save()
    p2 = Connector(name="P14", p1=12.46, p2=4.9, p3=14, p4=2.7, min_m1=15,
                   info="Clamex P-14, der Nachfolger des erfolgreichen Clamex P-15, ist ein zerlegbarer Verbindungs \
                            beschlag mit sekundenschneller formschlüssiger P-System Verankerung")
    p2.save()
    p3 = Connector(name="P1014", p1=12.46, p2=4.9, p3=14, p4=2.7, min_m1=15,
                   info="Clamex P Medius ist der Mittelwandverbinder passend zum Clamex P-14 Verbinder für Materialstärken ab 16mm")
    p3.save()
