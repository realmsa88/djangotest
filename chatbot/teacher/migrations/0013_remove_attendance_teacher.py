# Generated by Django 5.0.2 on 2024-06-15 07:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0012_remove_attendance_absence_title'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendance',
            name='teacher',
        ),
    ]