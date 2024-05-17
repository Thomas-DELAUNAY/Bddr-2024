# Generated by Django 4.1 on 2024-03-16 22:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("investigation", "0012_remove_email_email_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="addresseemail",
            name="email",
            field=models.OneToOneField(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="sender_email",
                to="investigation.email",
            ),
        ),
        migrations.AlterField(
            model_name="addresseemail",
            name="employee",
            field=models.ForeignKey(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="investigation.employee",
            ),
        ),
        migrations.AlterField(
            model_name="addresseemail",
            name="estInterne",
            field=models.BooleanField(default=False),
        ),
    ]