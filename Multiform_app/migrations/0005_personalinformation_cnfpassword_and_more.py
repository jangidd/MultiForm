# Generated by Django 4.2.13 on 2024-07-01 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Multiform_app", "0004_personalinformation_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="personalinformation",
            name="cnfpassword",
            field=models.CharField(blank=True, default=None, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name="personalinformation",
            name="password",
            field=models.CharField(blank=True, default=None, max_length=15, null=True),
        ),
    ]