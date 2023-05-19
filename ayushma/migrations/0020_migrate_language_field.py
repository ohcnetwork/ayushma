from django.db import migrations, models
from ayushma.utils.language_helpers import translate_text


def migrate_language(apps, schema_editor):
    chatMessage_model = apps.get_model("ayushma", "ChatMessage")
    updated_chat_messages = []

    for chat_message in chatMessage_model.objects.all():
        language = chat_message.chat.language
        message = chat_message.message
        translated_message = message
        if language != "en":
            translated_message = translate_text(message, language)
        chat_message.translated_message = translated_message
        chat_message.language = language
        updated_chat_messages.append(chat_message)

    chatMessage_model.objects.bulk_update(
        updated_chat_messages,
        ["translated_message", "language"],
    )


def reverse_migrate_language(apps, schema_editor):
    chatMessage_model = apps.get_model("ayushma", "ChatMessage")
    chat_model = apps.get_model("ayushma", "Chat")

    reverted_chat_messages = []
    for chatMessage in chatMessage_model.objects.all():
        chatMessage.chat.language = chatMessage.language
        reverted_chat_messages.append(chatMessage.chat)

    chat_model.objects.bulk_update(reverted_chat_messages, ["language"])


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
            name="translated_message",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.RunPython(migrate_language, reverse_migrate_language),
        migrations.RemoveField(
            model_name="chat",
            name="language",
        ),
    ]
