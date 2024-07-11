# Generated by Django 4.2.13 on 2024-06-29 07:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="PersonalInformation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("first_name", models.CharField(max_length=50)),
                ("last_name", models.CharField(max_length=50)),
                ("email", models.EmailField(max_length=254)),
                ("address", models.CharField(max_length=200)),
                ("contact_no", models.CharField(max_length=15)),
                ("resume", models.FileField(upload_to="uploads/")),
                ("photo", models.ImageField(upload_to="uploads/")),
                ("experience_years", models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="ReportingAreaDetails",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("mriopt", models.CharField(max_length=100)),
                ("mriothers", models.CharField(max_length=100)),
                ("ctopt", models.CharField(max_length=100)),
                ("ctothers", models.CharField(max_length=100)),
                ("xray", models.BooleanField()),
                ("others", models.BooleanField()),
                (
                    "personal_information",
                    models.ForeignKey(
                        default=None,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="Multiform_app.personalinformation",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ExperienceDetails",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "exinstitution1",
                    models.CharField(
                        blank=True, default=None, max_length=30, null=True
                    ),
                ),
                ("exstdate1", models.DateField(blank=True, default=None, null=True)),
                ("exenddate1", models.DateField(blank=True, default=None, null=True)),
                (
                    "exinstitution2",
                    models.CharField(
                        blank=True, default=None, max_length=30, null=True
                    ),
                ),
                ("exstdate2", models.DateField(blank=True, default=None, null=True)),
                ("exenddate2", models.DateField(blank=True, default=None, null=True)),
                (
                    "exinstitution3",
                    models.CharField(
                        blank=True, default=None, max_length=30, null=True
                    ),
                ),
                ("exstdate3", models.DateField(blank=True, default=None, null=True)),
                ("exenddate3", models.DateField(blank=True, default=None, null=True)),
                (
                    "personal_information",
                    models.ForeignKey(
                        default=None,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="Multiform_app.personalinformation",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="EducationalDetails",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("tenthname", models.CharField(max_length=30)),
                ("tenthgrade", models.CharField(max_length=10)),
                ("tenthpsyr", models.CharField(max_length=15)),
                ("tenthcertificate", models.FileField(upload_to="uploads/")),
                ("twelthname", models.CharField(max_length=30)),
                ("twelthgrade", models.CharField(max_length=10)),
                ("twelthpsyr", models.CharField(max_length=15)),
                ("twelthcertificate", models.FileField(upload_to="uploads/")),
                ("mbbsinstitution", models.CharField(max_length=25)),
                ("mbbsgrade", models.CharField(max_length=10)),
                ("mbbspsyr", models.CharField(max_length=10)),
                ("mbbsmarksheet", models.FileField(upload_to="uploads/")),
                ("mbbsdegree", models.FileField(upload_to="uploads/")),
                ("mdinstitution", models.CharField(max_length=25)),
                ("mdgrade", models.CharField(max_length=10)),
                ("mdpsyr", models.CharField(max_length=10)),
                ("mdmarksheet", models.FileField(upload_to="uploads/")),
                ("mddegree", models.FileField(upload_to="uploads/")),
                ("videofile", models.FileField(upload_to="uploads/")),
                (
                    "personal_information",
                    models.ForeignKey(
                        default=None,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="Multiform_app.personalinformation",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="BankingDetails",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("accholdername", models.CharField(max_length=25)),
                ("bankname", models.CharField(max_length=25)),
                ("branchname", models.CharField(max_length=25)),
                ("acnumber", models.CharField(max_length=15)),
                ("ifsc", models.CharField(max_length=15)),
                ("pancardno", models.CharField(max_length=10)),
                ("aadharcardno", models.CharField(max_length=12)),
                ("pancard", models.FileField(upload_to="uploads/")),
                ("aadharcard", models.FileField(upload_to="uploads/")),
                ("cheque", models.FileField(upload_to="uploads/")),
                (
                    "personal_information",
                    models.ForeignKey(
                        default=None,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="Multiform_app.personalinformation",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="AvailabilityDetails",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("monday", models.BooleanField()),
                ("tuesday", models.BooleanField()),
                ("wednesday", models.BooleanField()),
                ("thursday", models.BooleanField()),
                ("friday", models.BooleanField()),
                ("saturday", models.BooleanField()),
                ("sunday", models.BooleanField()),
                ("monst", models.CharField(default="Individual", max_length=255)),
                ("monend", models.CharField(default="Individual", max_length=255)),
                ("tuest", models.CharField(default="Individual", max_length=255)),
                ("tueend", models.CharField(default="Individual", max_length=255)),
                ("wedst", models.CharField(default="Individual", max_length=255)),
                ("wedend", models.CharField(default="Individual", max_length=255)),
                ("thust", models.CharField(default="Individual", max_length=255)),
                ("thuend", models.CharField(default="Individual", max_length=255)),
                ("frist", models.CharField(default="Individual", max_length=255)),
                ("friend", models.CharField(default="Individual", max_length=255)),
                ("satst", models.CharField(default="Individual", max_length=255)),
                ("satend", models.CharField(default="Individual", max_length=255)),
                ("sunst", models.CharField(default="Individual", max_length=255)),
                ("sunend", models.CharField(default="Individual", max_length=255)),
                (
                    "personal_information",
                    models.ForeignKey(
                        default=None,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="Multiform_app.personalinformation",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="AchievementDetails",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "award1",
                    models.CharField(
                        blank=True, default=None, max_length=30, null=True
                    ),
                ),
                ("awarddate1", models.DateField(blank=True, default=None, null=True)),
                (
                    "award2",
                    models.CharField(
                        blank=True, default=None, max_length=30, null=True
                    ),
                ),
                ("awarddate2", models.DateField(blank=True, default=None, null=True)),
                (
                    "publishlink",
                    models.CharField(
                        blank=True, default=None, max_length=30, null=True
                    ),
                ),
                (
                    "personal_information",
                    models.ForeignKey(
                        default=None,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="Multiform_app.personalinformation",
                    ),
                ),
            ],
        ),
    ]