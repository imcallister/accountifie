# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Day',
            fields=[
                ('id', models.DateField(serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Month',
            fields=[
                ('id', models.CharField(help_text=b'e.g. "2009M04"', max_length=7, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Quarter',
            fields=[
                ('id', models.CharField(help_text=b'e.g. "2009Q1"', max_length=6, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Week',
            fields=[
                ('id', models.CharField(max_length=7, serialize=False, primary_key=True)),
                ('first_day', models.DateField(null=True)),
                ('last_day', models.DateField(null=True)),
                ('end_month', models.ForeignKey(related_name='end_week_set', to='cal.Month', on_delete=models.CASCADE)),
                ('start_month', models.ForeignKey(related_name='start_week_set', to='cal.Month', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Year',
            fields=[
                ('id', models.IntegerField(help_text=b'4 digit year e.g. 2009', serialize=False, primary_key=True)),
            ],
        ),
        migrations.AddField(
            model_name='week',
            name='year',
            field=models.ForeignKey(to='cal.Year', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='quarter',
            name='year',
            field=models.ForeignKey(to='cal.Year', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='month',
            name='quarter',
            field=models.ForeignKey(to='cal.Quarter', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='month',
            name='year',
            field=models.ForeignKey(to='cal.Year', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='day',
            name='month',
            field=models.ForeignKey(to='cal.Month', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='day',
            name='quarter',
            field=models.ForeignKey(to='cal.Quarter', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='day',
            name='year',
            field=models.ForeignKey(to='cal.Year', on_delete=models.CASCADE),
        ),
    ]
