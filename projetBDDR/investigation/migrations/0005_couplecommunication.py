# Generated by Django 4.1 on 2024-05-01 22:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("investigation", "0004_rename_estinterne_addresseemail_estinterne"),
    ]

    operations = [
        migrations.CreateModel(
            name="CoupleCommunication",
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
                ("employee_id_1", models.CharField(max_length=100)),
                ("employee_id_2", models.CharField(max_length=100)),
                ("total_mails_echanges", models.IntegerField()),
            ],
            options={
                "unique_together": {
                    ("employee_id_1", "employee_id_2", "total_mails_echanges")
                },
            },
        ),
    ]
