# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forecasts', '0002_forecast_metrics'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='forecast',
            name='metrics',
        ),
    ]
