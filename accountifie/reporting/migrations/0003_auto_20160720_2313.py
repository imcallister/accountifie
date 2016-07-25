# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0002_metricentry_as_of'),
    ]

    operations = [
        migrations.AlterField(
            model_name='metricentry',
            name='as_of',
            field=models.DateField(db_index=True),
        ),
    ]
