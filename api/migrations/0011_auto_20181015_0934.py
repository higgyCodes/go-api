# Generated by Django 2.0.8 on 2018-10-15 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_auto_20181008_0950'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gdacsevent',
            name='vulnerability',
            field=models.FloatField(),
        ),
    ]