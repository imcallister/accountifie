# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GLSnapshot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('snapped_at', models.DateTimeField()),
                ('short_desc', models.CharField(max_length=100)),
                ('comment', models.TextField()),
                ('closing_date', models.DateField()),
            ],
        ),
    ]
