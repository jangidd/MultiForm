# Generated by Django 4.2.13 on 2024-07-06 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Multiform_app", "0013_rename_fritime_availabilitydetails_endtime1_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="personalinformation",
            name="updatemessage1",
            field=models.CharField(blank=True, default=None, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="personalinformation",
            name="updatemessage2",
            field=models.CharField(blank=True, default=None, max_length=100, null=True),
        ),
    ]