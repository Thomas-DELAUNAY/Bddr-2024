# Generated by Django 4.1 on 2024-04-10 16:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("investigation", "0021_alter_receiversmail_unique_together"),
    ]

    operations = [
        migrations.RenameField(
            model_name="email",
            old_name="contenu",
            new_name="content",
        ),
    ]
