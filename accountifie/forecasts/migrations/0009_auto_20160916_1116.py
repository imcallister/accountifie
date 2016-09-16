# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forecasts', '0008_auto_20160916_1108'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forecast',
            name='model',
            field=models.TextField(blank=True),
        ),
    ]
