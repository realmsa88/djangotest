# Generated by Django 5.0.2 on 2024-05-28 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0002_remove_progressbar_result_progressbar_stars_received'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='progressbar',
            name='stars_received',
        ),
        migrations.AddField(
            model_name='progressbar',
            name='result',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
