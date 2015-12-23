# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gl', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.CharField(max_length=12, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'gl_project',
                'verbose_name_plural': 'Projects',
            },
        ),
        migrations.AddField(
            model_name='tranline',
            name='project',
            field=models.ForeignKey(blank=True, to='gl.Project', null=True),
        ),
    ]
