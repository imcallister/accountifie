"""Date objects all nicely joinable together to allow SQL GROUP BY.

The calendar actually gets constructed by functions in __init__.py
"""
from datetime import date
from django.db import models


class Year(models.Model):
    id = models.IntegerField(primary_key=True, help_text="4 digit year e.g. 2009")
    def __unicode__(self):
        return str(self.id)
        
class Quarter(models.Model):
    id = models.CharField(primary_key=True, max_length=6, help_text='e.g. "2009Q1"')
    year = models.ForeignKey(Year, db_index=True, on_delete=models.CASCADE)
    def __unicode__(self):
        return self.id
    
class Month(models.Model):
    id = models.CharField(primary_key=True, max_length=7, help_text='e.g. "2009M04"')
    quarter = models.ForeignKey(Quarter, db_index=True, on_delete=models.CASCADE)
    year = models.ForeignKey(Year, db_index=True, on_delete=models.CASCADE)
    def __unicode__(self):
        return str(self.id)
        
    def first_of_month(self):
        yyyy, mm = self.id.split('M')
        return date(int(yyyy), int(mm), 1)
    
    def day_of_month(self, day):
        yyyy, mm = self.id.split('M')
        return date(int(yyyy), int(mm), day)

class Week(models.Model):
    "Identified by YYYYWNN  e.g. 2007W29"
    id = models.CharField(primary_key=True, max_length=7)
    first_day = models.DateField(null=True)  #can be last year, hard to initialize in a new system
    last_day = models.DateField(null=True) #can be next year, hard to initialize at end of year
    start_month = models.ForeignKey(Month, related_name='start_week_set', on_delete=models.CASCADE)
    end_month = models.ForeignKey(Month, related_name='end_week_set', on_delete=models.CASCADE)
    year = models.ForeignKey(Year, on_delete=models.CASCADE)
    def __unicode__(self):
        return str(self.id)

class Day(models.Model):
    id = models.DateField(primary_key=True)
    month = models.ForeignKey(Month, db_index=True, on_delete=models.CASCADE)
    quarter = models.ForeignKey(Quarter, db_index=True, on_delete=models.CASCADE)
    year = models.ForeignKey(Year, db_index=True, on_delete=models.CASCADE)
    def __unicode__(self):
        return '%04d-%02d-%02d' % (self.id.year, self.id.month, self.id.day)
    
