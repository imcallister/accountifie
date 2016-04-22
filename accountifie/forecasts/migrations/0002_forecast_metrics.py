# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('forecasts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='forecast',
            name='metrics',
            field=jsonfield.fields.JSONField(default=dict, blank=True),
        ),
    ]
