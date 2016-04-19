# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('snapshot', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='glsnapshot',
            name='snapped_at',
            field=models.DateTimeField(help_text=b'Local NY time'),
        ),
    ]
