# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gl', '0006_auto_20171221_0736'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='label',
            field=models.CharField(default=b'TBD', max_length=20),
        ),
        migrations.AddField(
            model_name='counterparty',
            name='label',
            field=models.CharField(default=b'TBD', max_length=20),
        ),
    ]
