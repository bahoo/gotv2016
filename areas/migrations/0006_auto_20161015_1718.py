# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-15 17:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('areas', '0005_auto_20161013_0228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='precinctcoordinator',
            name='area',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='areas.Area'),
        ),
    ]
