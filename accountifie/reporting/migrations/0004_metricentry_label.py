# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0003_auto_20160720_2313'),
    ]

    operations = [
        migrations.AddField(
            model_name='metricentry',
            name='label',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
    ]
