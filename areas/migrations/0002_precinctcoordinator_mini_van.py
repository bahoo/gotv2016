# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-15 16:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('areas', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='precinctcoordinator',
            name='mini_van',
            field=models.BooleanField(default=False),
        ),
    ]
