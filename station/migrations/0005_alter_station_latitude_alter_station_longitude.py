# Generated by Django 4.2.6 on 2023-10-19 09:29

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("station", "0004_alter_ticket_options_alter_ticket_unique_together"),
    ]

    operations = [
        migrations.AlterField(
            model_name="station",
            name="latitude",
            field=models.FloatField(
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(-90.0),
                    django.core.validators.MaxValueValidator(90.0),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="station",
            name="longitude",
            field=models.FloatField(
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(-180.0),
                    django.core.validators.MaxValueValidator(180.0),
                ],
            ),
        ),
    ]
