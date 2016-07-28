# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0004_metricentry_label'),
        ('gl', '0002_transaction_bmo_id'),
        ('forecasts', '0003_remove_forecast_metrics'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectionModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('description', models.TextField()),
                ('as_of', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='ProjModelv1Param',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('frequency', models.CharField(max_length=20, choices=[(b'MONTHLY', b'Monthly'), (b'QUARTERLY', b'Quarterly'), (b'ANNUAL', b'Annual'), (b'ONE-OFF', b'One-off')])),
                ('window', models.CharField(max_length=20, choices=[(b'M1', b'Previous Month'), (b'M3', b'Rolling 3-month'), (b'M12', b'Rolling 12-month'), (b'A1', b'12 Month Lag')])),
                ('scaling', models.CharField(max_length=20, choices=[(b'PROP', b'Proportional')])),
                ('account', models.ForeignKey(to='gl.Account')),
                ('counterparty', models.ForeignKey(to='gl.Counterparty')),
                ('metric', models.ForeignKey(to='reporting.Metric')),
            ],
        ),
    ]
