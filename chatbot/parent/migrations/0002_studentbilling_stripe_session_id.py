# Generated by Django 5.0.2 on 2024-06-28 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parent', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentbilling',
            name='stripe_session_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]