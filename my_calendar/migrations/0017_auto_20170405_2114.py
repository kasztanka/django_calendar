# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-05 21:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_calendar', '0016_auto_20170405_1919'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mycalendar',
            name='color',
            field=models.CharField(max_length=7),
        ),
    ]
