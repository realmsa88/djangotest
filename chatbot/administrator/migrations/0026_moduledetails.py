# Generated by Django 5.0.2 on 2024-05-22 08:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administrator', '0025_alter_album_activityid'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModuleDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module_type', models.CharField(max_length=255, null=True)),
                ('module_name', models.CharField(max_length=255, null=True)),
                ('description', models.CharField(max_length=255, null=True)),
                ('bookInstrument', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='administrator.bookinstrument')),
            ],
        ),
    ]
