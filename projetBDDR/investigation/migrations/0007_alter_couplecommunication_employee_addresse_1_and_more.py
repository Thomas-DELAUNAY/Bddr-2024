# Generated by Django 4.1 on 2024-05-03 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "investigation",
            "0006_rename_employee_id_1_couplecommunication_employee_addresse_1_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="couplecommunication",
            name="employee_addresse_1",
            field=models.EmailField(max_length=100),
        ),
        migrations.AlterField(
            model_name="couplecommunication",
            name="employee_addresse_2",
            field=models.EmailField(max_length=100),
        ),
    ]