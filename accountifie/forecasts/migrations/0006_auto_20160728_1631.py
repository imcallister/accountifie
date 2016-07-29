# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forecasts', '0005_auto_20160728_1628'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projmodelv1param',
            name='proj_model',
            field=models.ForeignKey(to='forecasts.ProjectionModel'),
        ),
    ]
