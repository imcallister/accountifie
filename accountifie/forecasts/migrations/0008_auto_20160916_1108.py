# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import accountifie.toolkit.utils.gl_helpers


class Migration(migrations.Migration):

    dependencies = [
        ('gl', '0002_transaction_bmo_id'),
        ('forecasts', '0007_auto_20160729_1122'),
    ]

    operations = [
        migrations.RenameField(
            model_name='forecast',
            old_name='projections',
            new_name='hardcode_projections',
        ),
        migrations.RemoveField(
            model_name='forecast',
            name='color_code',
        ),
        migrations.AddField(
            model_name='forecast',
            name='company',
            field=models.ForeignKey(default=accountifie.toolkit.utils.gl_helpers.get_default_company, to='gl.Company'),
        ),
        migrations.AddField(
            model_name='forecast',
            name='model',
            field=models.URLField(blank=True),
        ),
        migrations.AlterField(
            model_name='forecast',
            name='comment',
            field=models.TextField(blank=True),
        ),
    ]
