# Generated by Django 5.0.2 on 2024-04-30 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administrator', '0009_instrument_delete_primaryinstrument_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instrument',
            name='primary_name',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
