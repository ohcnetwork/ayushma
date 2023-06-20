# Generated by Django 4.1.7 on 2023-06-19 19:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ayushma", "0027_remove_chatmessage_ayushma_audio_url_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="stt_engine",
            field=models.CharField(
                choices=[("google", "Google"), ("whisper", "Whisper")],
                default="whisper",
                max_length=50,
            ),
        ),
    ]