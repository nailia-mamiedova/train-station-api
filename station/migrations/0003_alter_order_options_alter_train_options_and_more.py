# Generated by Django 4.2.6 on 2023-10-15 10:02

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("station", "0002_trip_crews_alter_station_latitude_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="order",
            options={"ordering": ["-created_at"]},
        ),
        migrations.AlterModelOptions(
            name="train",
            options={"ordering": ["name"]},
        ),
        migrations.AlterModelOptions(
            name="trip",
            options={"ordering": ["-departure_time"]},
        ),
    ]
