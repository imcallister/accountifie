# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, null=True, blank=True)),
                ('company', models.CharField(max_length=100, null=True, blank=True)),
                ('address1', models.CharField(max_length=100, null=True, blank=True)),
                ('address2', models.CharField(max_length=100, null=True, blank=True)),
                ('city', models.CharField(max_length=50, null=True, blank=True)),
                ('postal_code', models.CharField(max_length=20, null=True, blank=True)),
                ('province', models.CharField(max_length=30, null=True, blank=True)),
                ('country', models.CharField(max_length=30, null=True, blank=True)),
                ('phone', models.CharField(max_length=30, null=True, blank=True)),
                ('email', models.EmailField(max_length=254, null=True, blank=True)),
            ],
        ),
    ]
