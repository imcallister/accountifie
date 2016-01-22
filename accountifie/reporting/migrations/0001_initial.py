# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Metric',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='MetricEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(db_index=True)),
                ('balance', models.DecimalField(max_digits=20, decimal_places=2)),
                ('metric', models.ForeignKey(blank=True, to='reporting.Metric', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ReportDef',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('path', models.CharField(max_length=200)),
            ],
            options={
                'db_table': 'reporting_reportdef',
            },
        ),
    ]
