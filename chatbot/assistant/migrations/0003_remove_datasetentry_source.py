# Generated by Django 5.0.2 on 2024-03-17 02:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assistant', '0002_datasetentry'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datasetentry',
            name='source',
        ),
    ]
