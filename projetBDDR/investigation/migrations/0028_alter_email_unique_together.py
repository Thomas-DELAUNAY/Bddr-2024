# Generated by Django 4.1 on 2024-04-14 11:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("investigation", "0027_alter_email_date"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="email",
            unique_together=set(),
        ),
    ]
