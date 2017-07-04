# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-04 13:30
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=200, unique=True)),
                ('name', models.CharField(max_length=200, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='CRM',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(max_length=200, unique=True)),
                ('state', models.CharField(choices=[('draft', 'Draft'), ('downpay', 'Downpay'), ('late', 'Late'), ('normal', 'Normal'), ('defaulted', 'Defaulted'), ('repo', 'Repossessed')], default='draft', max_length=200)),
                ('payg', models.NullBooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='CRMProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField(default=datetime.datetime(2017, 7, 4, 13, 30, 40, 371707))),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('enable_state', models.CharField(choices=[('enabled', 'Enabled'), ('disabled', 'Disabled')], default='disabled', max_length=200)),
                ('condition', models.CharField(choices=[('normal', 'Normal'), ('damaged', 'Damaged')], default='normal', max_length=200)),
                ('serial_number', models.CharField(blank=True, max_length=200, null=True)),
                ('imei', models.CharField(blank=True, max_length=200, null=True)),
                ('active', models.BooleanField(default=True)),
                ('price_unit', models.FloatField(blank=True, null=True)),
                ('quantity', models.FloatField(blank=True, null=True)),
                ('crm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.CRM')),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(max_length=200, unique=True)),
                ('first', models.CharField(blank=True, max_length=200, null=True)),
                ('last', models.CharField(blank=True, max_length=200, null=True)),
                ('city', models.CharField(max_length=200)),
                ('street', models.CharField(max_length=200)),
                ('street2', models.CharField(blank=True, max_length=200, null=True)),
                ('zip', models.CharField(blank=True, max_length=200, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('phone', models.CharField(blank=True, max_length=200, null=True)),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.Country')),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('default_code', models.CharField(max_length=200, unique=True)),
                ('list_price', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('city', models.CharField(max_length=200)),
                ('street', models.CharField(max_length=200)),
                ('street2', models.CharField(blank=True, max_length=200, null=True)),
                ('zip', models.CharField(max_length=200)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('phone', models.CharField(max_length=200)),
                ('payg', models.BooleanField(default=False)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.Company')),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.Country')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.Shop')),
            ],
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('city', models.CharField(max_length=200)),
                ('street', models.CharField(max_length=200)),
                ('street2', models.CharField(blank=True, max_length=200, null=True)),
                ('zip', models.CharField(max_length=200)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('phone', models.CharField(blank=True, max_length=200, null=True)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.Country')),
            ],
        ),
        migrations.AddField(
            model_name='employee',
            name='shop',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.Shop'),
        ),
        migrations.AddField(
            model_name='crmproduct',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.Product'),
        ),
        migrations.AddField(
            model_name='crm',
            name='crm_products',
            field=models.ManyToManyField(blank=True, null=True, through='shop.CRMProduct', to='shop.Product'),
        ),
        migrations.AddField(
            model_name='crm',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.Customer'),
        ),
        migrations.AddField(
            model_name='crm',
            name='shop',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.Shop'),
        ),
        migrations.AddField(
            model_name='company',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.Country'),
        ),
    ]
