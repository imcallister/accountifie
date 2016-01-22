# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DeferredTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pid', models.IntegerField(help_text=b'pid of the process')),
                ('start', models.DateTimeField()),
                ('finish', models.DateTimeField(null=True)),
                ('task', models.CharField(default=b'', max_length=512)),
                ('args', models.CharField(default=b'', max_length=512)),
                ('kwds', models.CharField(default=b'', max_length=512)),
                ('result', models.CharField(max_length=512, null=True)),
                ('finished', models.BooleanField(default=False)),
                ('stdout', models.TextField(default=b'')),
                ('stderr', models.TextField(default=b'')),
                ('success', models.BooleanField(default=False)),
                ('hashcode', models.CharField(default=b'', max_length=32)),
                ('status', models.CharField(default=b'', max_length=256)),
                ('progress', models.PositiveSmallIntegerField(default=b'')),
                ('username', models.CharField(default=b'', max_length=30)),
                ('success_url', models.CharField(default=b'', max_length=256, blank=True)),
                ('title', models.CharField(max_length=256, blank=True)),
            ],
        ),
    ]
