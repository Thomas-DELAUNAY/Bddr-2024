# Generated by Django 4.1 on 2024-04-11 13:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("investigation", "0025_alter_receiversmail_unique_together"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="email",
            unique_together={("id",)},
        ),
    ]
