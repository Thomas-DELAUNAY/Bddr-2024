# Generated by Django 4.1 on 2024-03-23 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("investigation", "0015_alter_receiversmail_unique_together"),
    ]

    operations = [
        migrations.AlterField(
            model_name="email",
            name="dateSend",
            field=models.DateField(),
        ),
    ]
