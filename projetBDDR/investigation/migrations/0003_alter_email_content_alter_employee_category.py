# Generated by Django 4.1 on 2024-05-22 11:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("investigation", "0002_alter_email_date_alter_email_subject"),
    ]

    operations = [
        migrations.AlterField(
            model_name="email",
            name="content",
            field=models.TextField(default="", null=True),
        ),
        migrations.AlterField(
            model_name="employee",
            name="category",
            field=models.ForeignKey(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="investigation.groupe",
            ),
        ),
    ]
