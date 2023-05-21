from django.db import migrations, models


def migrate_language(apps, schema_editor):
    chatMessage_model = apps.get_model("ayushma", "ChatMessage")
    updated_chat_messages = []

    for chat_message in chatMessage_model.objects.all():
        chat_message.original_message = chat_message.message
        chat_message.language = chat_message.chat.language
        updated_chat_messages.append(chat_message)

    chatMessage_model.objects.bulk_update(
        updated_chat_messages,
        ["original_message", "language"],
    )


class Migration(migrations.Migration):
    dependencies = [
        ("ayushma", "0019_remove_chatmessage_audio_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="chatmessage",
            name="language",
            field=models.CharField(default="en", max_length=10),
        ),
        migrations.AddField(
            model_name="chatmessage",
            name="original_message",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.RunPython(migrate_language, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="chat",
            name="language",
        ),
    ]
