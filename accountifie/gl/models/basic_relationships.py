from colorful.fields import RGBColorField

from django.db import models



class Company(models.Model):
    id = models.CharField(max_length=5, primary_key=True)
    name = models.CharField(max_length=50)
    cmpy_type = models.CharField(max_length=10, choices=[('ALO', 'Standalone'),('CON', 'Consolidation'),])
    color_code = RGBColorField(blank=True)

    subs = models.ManyToManyField('self', blank=True, related_name="+")

    class Meta:
        verbose_name_plural = 'Companies'
        app_label = 'gl'
        db_table = 'gl_company'

    def __str__(self):
        return self.id

class Counterparty(models.Model):
    id = models.CharField(max_length=12, primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Counterparties'
        app_label = 'gl'
        db_table = 'gl_counterparty'

    def __str__(self):
        return self.id

class Project(models.Model):
    id = models.CharField(max_length=12, primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Projects'
        app_label = 'gl'
        db_table = 'gl_project'

    def __str__(self):
        return self.id

class Department(models.Model):
    #PK is id, that's OK
    name = models.CharField(max_length=25, unique=True)

    class Meta:
        app_label = 'gl'
        db_table = 'gl_department'

    def __unicode__(self):
        return '%d: %s' % (self.id, self.name)


class Employee(models.Model):
    employee_id = models.IntegerField(primary_key=True)
    ach = models.CharField(max_length=200, null=True)
    usr_disable = models.BooleanField()
    e_mail = models.CharField(max_length=200, null=True)
    role = models.CharField(max_length=200, null=True)
    employee_name = models.CharField(max_length=200, null=True)
    department = models.ForeignKey(Department)
    p_card = models.CharField(max_length=200, null=True)

    class Meta:
        app_label = 'gl'
        db_table = 'gl_employee'

    def __str__(self):
        return '%s'  % (self.employee_name)

class ExternalAccount(models.Model):
    company = models.ForeignKey('gl.Company')
    gl_account = models.ForeignKey('gl.Account')
    counterparty = models.ForeignKey('gl.Counterparty')
    label = models.CharField(max_length=10)
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'gl'
        db_table = 'gl_externalaccount'

    def __str__(self):
        return self.label
