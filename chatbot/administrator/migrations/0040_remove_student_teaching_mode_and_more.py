# Generated by Django 5.0.2 on 2024-06-29 10:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('administrator', '0039_billing'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='teaching_mode',
        ),
        migrations.RemoveField(
            model_name='teacher',
            name='teachingmode',
        ),
        migrations.DeleteModel(
            name='TeachingMode',
        ),
    ]
