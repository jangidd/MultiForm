# Generated by Django 4.2.13 on 2024-06-30 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Multiform_app", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="educationaldetails",
            name="mbbspsyr",
            field=models.DateField(max_length=10),
        ),
        migrations.AlterField(
            model_name="educationaldetails",
            name="mdpsyr",
            field=models.DateField(max_length=10),
        ),
        migrations.AlterField(
            model_name="educationaldetails",
            name="tenthpsyr",
            field=models.DateField(max_length=15),
        ),
        migrations.AlterField(
            model_name="educationaldetails",
            name="twelthpsyr",
            field=models.DateField(max_length=15),
        ),
    ]
