from django.db import models
import datetime


class Metric(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class MetricEntry(models.Model):
    metric = models.ForeignKey(Metric, null=True, blank=True)
    label = models.CharField(max_length=20, null=True, blank=True)
    date = models.DateField(db_index=True)
    as_of = models.DateField(db_index=True)
    balance = models.DecimalField(max_digits=20, decimal_places=2)
