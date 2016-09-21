# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forecasts', '0009_auto_20160916_1116'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projmodelv1param',
            name='account',
        ),
        migrations.RemoveField(
            model_name='projmodelv1param',
            name='contra',
        ),
        migrations.RemoveField(
            model_name='projmodelv1param',
            name='counterparty',
        ),
        migrations.RemoveField(
            model_name='projmodelv1param',
            name='metric',
        ),
        migrations.RemoveField(
            model_name='projmodelv1param',
            name='proj_model',
        ),
        migrations.DeleteModel(
            name='ProjectionModel',
        ),
        migrations.DeleteModel(
            name='ProjModelv1Param',
        ),
    ]
