# -*- coding: utf-8 -*-


from django.db import migrations, models
import colorful.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.CharField(help_text=b'Unique short code or number', max_length=20, serialize=False, primary_key=True)),
                ('path', models.CharField(help_text=b'dotted-path reference to show location on balance sheet', unique=True, max_length=100, db_index=True)),
                ('ordering', models.IntegerField(default=0)),
                ('display_name', models.CharField(help_text=b'the name you would use on a report title', max_length=100, blank=True)),
                ('role', models.CharField(help_text=b'used in P&L queries and for picklists', max_length=10, choices=[(b'asset', b'asset'), (b'liability', b'liability'), (b'income', b'income'), (b'expense', b'expense'), (b'capital', b'capital')])),
            ],
            options={
                'ordering': ('id',),
                'db_table': 'gl_account',
            },
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.CharField(max_length=5, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('cmpy_type', models.CharField(max_length=10, choices=[(b'ALO', b'Standalone'), (b'CON', b'Consolidation')])),
                ('color_code', colorful.fields.RGBColorField(blank=True)),
                ('subs', models.ManyToManyField(related_name='_company_subs_+', to='gl.Company', blank=True)),
            ],
            options={
                'db_table': 'gl_company',
                'verbose_name_plural': 'Companies',
            },
        ),
        migrations.CreateModel(
            name='Counterparty',
            fields=[
                ('id', models.CharField(max_length=12, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'gl_counterparty',
                'verbose_name_plural': 'Counterparties',
            },
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=25)),
            ],
            options={
                'db_table': 'gl_department',
            },
        ),
        migrations.CreateModel(
            name='DepreciationPolicy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('depreciation_period', models.PositiveIntegerField()),
                ('cap_account', models.ForeignKey(related_name='deppolicy_acct', to='gl.Account', on_delete=models.CASCADE)),
                ('depreciation_account', models.ForeignKey(related_name='deppolicy_depacct', to='gl.Account', on_delete=models.CASCADE)),
            ],
            options={
                'db_table': 'gl_depreciationpolicy',
            },
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('employee_id', models.IntegerField(serialize=False, primary_key=True)),
                ('ach', models.CharField(max_length=200, null=True)),
                ('usr_disable', models.BooleanField()),
                ('e_mail', models.CharField(max_length=200, null=True)),
                ('role', models.CharField(max_length=200, null=True)),
                ('employee_name', models.CharField(max_length=200, null=True)),
                ('p_card', models.CharField(max_length=200, null=True)),
                ('department', models.ForeignKey(to='gl.Department', on_delete=models.CASCADE)),
            ],
            options={
                'db_table': 'gl_employee',
            },
        ),
        migrations.CreateModel(
            name='ExternalAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=100)),
                ('company', models.ForeignKey(to='gl.Company', on_delete=models.CASCADE)),
                ('counterparty', models.ForeignKey(to='gl.Counterparty', on_delete=models.CASCADE)),
                ('gl_account', models.ForeignKey(to='gl.Account', on_delete=models.CASCADE)),
            ],
            options={
                'db_table': 'gl_externalaccount',
            },
        ),
        migrations.CreateModel(
            name='ExternalBalance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(db_index=True)),
                ('balance', models.DecimalField(max_digits=11, decimal_places=2)),
                ('comment', models.CharField(max_length=100, null=True, blank=True)),
                ('account', models.ForeignKey(to='gl.Account', on_delete=models.CASCADE)),
                ('company', models.ForeignKey(to='gl.Company', on_delete=models.CASCADE)),
            ],
            options={
                'db_table': 'gl_externalbalance',
            },
        ),
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
        migrations.CreateModel(
            name='TranLine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(max_digits=11, decimal_places=2)),
                ('tags', models.CharField(max_length=200, blank=True)),
                ('account', models.ForeignKey(to='gl.Account', on_delete=models.CASCADE)),
                ('counterparty', models.ForeignKey(blank=True, to='gl.Counterparty', null=True, on_delete=models.CASCADE)),
            ],
            options={
                'db_table': 'gl_tranline',
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(db_index=True)),
                ('date_end', models.DateField(db_index=True, null=True, blank=True)),
                ('comment', models.CharField(max_length=100)),
                ('long_desc', models.CharField(max_length=200, null=True, blank=True)),
                ('object_id', models.PositiveIntegerField()),
                ('company', models.ForeignKey(to='gl.Company', on_delete=models.CASCADE)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', on_delete=models.CASCADE)),
            ],
            options={
                'db_table': 'gl_transaction',
            },
        ),
        migrations.AddField(
            model_name='tranline',
            name='transaction',
            field=models.ForeignKey(to='gl.Transaction', on_delete=models.CASCADE),
        ),
    ]
