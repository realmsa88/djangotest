# Generated by Django 5.0.2 on 2024-06-05 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0008_attendance_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='description',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='title',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
