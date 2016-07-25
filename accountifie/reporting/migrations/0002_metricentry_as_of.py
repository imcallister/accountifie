# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='metricentry',
            name='as_of',
            field=models.DateField(default=datetime.date(2016, 7, 19), db_index=True),
        ),
    ]
