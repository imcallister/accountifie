# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forecasts', '0004_projectionmodel_projmodelv1param'),
    ]

    operations = [
        migrations.AddField(
            model_name='projmodelv1param',
            name='label',
            field=models.CharField(default='', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='projmodelv1param',
            name='proj_model',
            field=models.ForeignKey(to='forecasts.ProjectionModel', null=True),
        ),
    ]
