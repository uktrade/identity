# Generated by Django 5.1.4 on 2025-01-02 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("profiles", "0003_alter_staffssoprofileemail_unique_together_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="historicalprofile",
            old_name="preferred_email",
            new_name="primary_email",
        ),
        migrations.RenameField(
            model_name="historicalstaffssoprofileemail",
            old_name="preferred",
            new_name="is_primary",
        ),
        migrations.RenameField(
            model_name="profile",
            old_name="preferred_email",
            new_name="primary_email",
        ),
        migrations.RenameField(
            model_name="staffssoprofileemail",
            old_name="preferred",
            new_name="is_primary",
        ),
        migrations.RemoveField(
            model_name="historicalstaffssoprofileemail",
            name="type",
        ),
        migrations.AlterUniqueTogether(
            name="staffssoprofileemail",
            unique_together={("profile", "email")},
        ),
        migrations.AddField(
            model_name="historicalprofile",
            name="contact_email",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="historicalstaffssoprofileemail",
            name="is_contact",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="profile",
            name="contact_email",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="staffssoprofileemail",
            name="is_contact",
            field=models.BooleanField(default=False),
        ),
        migrations.RemoveField(
            model_name="staffssoprofileemail",
            name="type",
        ),
    ]
