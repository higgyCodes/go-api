# Generated by Django 2.2.9 on 2020-02-12 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0044_reversiondifferencelog'),
    ]

    operations = [
        migrations.AddField(
            model_name='reversiondifferencelog',
            name='object_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='reversiondifferencelog',
            name='object_type',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
