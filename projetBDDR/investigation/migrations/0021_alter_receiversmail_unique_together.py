# Generated by Django 4.1 on 2024-04-07 12:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("investigation", "0020_alter_receiversmail_unique_together"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="receiversmail",
            unique_together=set(),
        ),
    ]