# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gl', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='bmo_id',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]
