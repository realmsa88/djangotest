# Generated by Django 5.0.2 on 2024-06-15 07:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administrator', '0035_rename_current_book_student_book'),
        ('teacher', '0013_remove_attendance_teacher'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='teacher',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='administrator.teacher'),
            preserve_default=False,
        ),
    ]
