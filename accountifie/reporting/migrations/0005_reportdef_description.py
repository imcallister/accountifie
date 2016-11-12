# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0004_metricentry_label'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportdef',
            name='description',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]
