from django.db import models

CALC_TYPES = [('as_of', 'Point in Time'),
			  ('diff', 'Change Over Time')]

class ReportDef(models.Model):
    name = models.CharField(max_length=50)
    path = models.CharField(max_length=200)
    description = models.CharField(max_length=100)
    calc_type = models.CharField(max_length=20, choices=CALC_TYPES)

    class Meta:
        app_label = 'reporting'
        db_table = 'reporting_reportdef'
    
    def __str__(self):
        return self.name

