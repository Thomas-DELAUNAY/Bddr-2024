# Generated by Django 4.1 on 2024-03-15 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("investigation", "0005_alter_email_email_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="email",
            name="email_id",
            field=models.CharField(
                default=None, max_length=200, null=True, unique=True
            ),
        ),
    ]