# Generated by Django 4.2.1 on 2023-09-04 13:02

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ayushma", "0041_merge_20230904_0908"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="preset_questions",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(), blank=True, null=True, size=None
            ),
        ),
    ]