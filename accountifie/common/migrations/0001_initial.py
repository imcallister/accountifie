# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('level', models.CharField(max_length=10)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('message', models.TextField()),
                ('traceback', models.TextField()),
                ('request', models.TextField()),
            ],
            options={
                'ordering': ['-time', 'id'],
                'verbose_name_plural': 'Log entries',
            },
        ),
        migrations.CreateModel(
            name='TaskMonitor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('task_id', models.CharField(max_length=200, null=True)),
                ('creation_timestamp', models.DateTimeField(auto_now_add=True, null=True)),
                ('task_name', models.CharField(max_length=200, null=True)),
                ('percent_complete', models.IntegerField(default=0, null=True)),
                ('task_state', models.CharField(max_length=200, null=True, choices=[(b'started', b'started'), (b'failed', b'failed'), (b'succeeded', b'succeeded')])),
                ('traceback', models.TextField(null=True)),
                ('log_info', models.TextField(null=True)),
                ('initiator', models.CharField(max_length=200, null=True)),
            ],
            options={
                'ordering': ['-creation_timestamp'],
            },
        ),
    ]
