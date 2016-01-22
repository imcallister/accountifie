# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields
import colorful.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Forecast',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=50, blank=True)),
                ('start_date', models.DateField()),
                ('color_code', colorful.fields.RGBColorField(blank=True)),
                ('projections', jsonfield.fields.JSONField(default=dict, blank=True)),
                ('comment', models.TextField()),
            ],
            options={
                'db_table': 'forecasts_forecast',
            },
        ),
    ]
