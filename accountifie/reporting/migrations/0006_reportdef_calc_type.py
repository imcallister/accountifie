# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0005_reportdef_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportdef',
            name='calc_type',
            field=models.CharField(default='as_of', max_length=20, choices=[(b'as_of', b'Point in Time'), (b'diff', b'Change Over Time')]),
            preserve_default=False,
        ),
    ]
