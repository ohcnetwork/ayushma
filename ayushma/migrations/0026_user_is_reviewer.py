# Generated by Django 4.1.7 on 2023-06-03 13:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ayushma", "0025_chat_prompt_alter_chat_project_alter_chat_user_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="is_reviewer",
            field=models.BooleanField(default=False),
        ),
    ]
