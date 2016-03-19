from django.db import models

class ReportDef(models.Model):
    name = models.CharField(max_length=50)
    path = models.CharField(max_length=200)

    class Meta:
        app_label = 'reporting'
        db_table = 'reporting_reportdef'
    
    def __str__(self):
        return self.name

