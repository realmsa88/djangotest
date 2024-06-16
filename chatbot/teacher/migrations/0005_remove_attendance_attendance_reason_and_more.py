# Generated by Django 5.0.2 on 2024-06-02 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0004_attendance'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendance',
            name='attendance_reason',
        ),
        migrations.RemoveField(
            model_name='attendance',
            name='attendance_title',
        ),
        migrations.AddField(
            model_name='attendance',
            name='attendance',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
