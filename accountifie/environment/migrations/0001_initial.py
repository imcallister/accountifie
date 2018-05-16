# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gl', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('display_as', models.CharField(max_length=100)),
                ('context', models.ForeignKey(blank=True, to='gl.Company', null=True, on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Variable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(unique=True, max_length=100)),
                ('value', models.CharField(unique=True, max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='config',
            name='reporting',
            field=models.ForeignKey(to='environment.Variable', on_delete=models.CASCADE),
        ),
    ]
