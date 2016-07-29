# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gl', '0002_transaction_bmo_id'),
        ('forecasts', '0006_auto_20160728_1631'),
    ]

    operations = [
        migrations.AddField(
            model_name='projmodelv1param',
            name='contra',
            field=models.ForeignKey(related_name='param_contra', default='1001', to='gl.Account'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='projmodelv1param',
            name='account',
            field=models.ForeignKey(related_name='param_account', to='gl.Account'),
        ),
    ]
