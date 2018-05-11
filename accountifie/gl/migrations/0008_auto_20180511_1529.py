# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('gl', '0007_auto_20180510_2236'),
    ]

    operations = [
        migrations.AlterField(
            model_name='counterparty',
            name='id',
            field=models.CharField(max_length=30, serialize=False, primary_key=True, validators=[django.core.validators.RegexValidator(b'^[0-9a-zA-Z]*$', b'Only alphanumeric characters are allowed. In particular.. no spaces.')]),
        ),
    ]
