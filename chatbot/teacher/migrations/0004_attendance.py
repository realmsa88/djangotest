# Generated by Django 5.0.2 on 2024-06-02 08:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administrator', '0032_remove_activity_recurring_weeks'),
        ('teacher', '0003_remove_progressbar_stars_received_progressbar_result'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attendance_title', models.CharField(max_length=255, null=True)),
                ('attendance_reason', models.CharField(max_length=255, null=True)),
                ('date', models.DateField(null=True)),
                ('time', models.TimeField(null=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='administrator.student')),
            ],
        ),
    ]