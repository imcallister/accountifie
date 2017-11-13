# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='label',
            field=models.CharField(default='Default', max_length=20),
            preserve_default=False,
        ),
    ]
