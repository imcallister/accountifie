# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('environment', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variable',
            name='value',
            field=models.CharField(max_length=100),
        ),
    ]
