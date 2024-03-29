# Generated by Django 5.0.3 on 2024-03-28 05:49

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Tasks",
            fields=[
                ("registration_time", models.DateTimeField()),
                (
                    "task_id",
                    models.CharField(max_length=150, primary_key=True, serialize=False),
                ),
                ("task_status", models.CharField(max_length=50)),
                ("result_destination", models.FilePathField()),
                ("queries_path", models.FilePathField()),
                ("model_settings", models.JSONField()),
            ],
            options={
                "verbose_name_plural": "Tasks",
            },
        ),
    ]