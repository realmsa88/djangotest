# Generated by Django 5.0.2 on 2024-04-30 10:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administrator', '0012_remove_teacher_instrument_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher',
            name='instrument',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='administrator.instrument'),
        ),
    ]
