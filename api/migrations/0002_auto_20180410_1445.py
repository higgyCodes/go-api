# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-04-10 14:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='snippet',
            name='snippet',
            field=models.TextField(),
        ),
    ]