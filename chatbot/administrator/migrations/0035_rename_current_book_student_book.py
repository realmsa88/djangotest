# Generated by Django 5.0.2 on 2024-06-13 10:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('administrator', '0034_teacherlogin'),
    ]

    operations = [
        migrations.RenameField(
            model_name='student',
            old_name='current_book',
            new_name='book',
        ),
    ]
