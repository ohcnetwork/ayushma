from rest_framework import serializers

from ayushma.models import Document


class DocumentSerializer(serializers.ModelSerializer):
    def validate(self, data):
        if not data.get("file") and not data.get("text_content"):
            raise serializers.ValidationError(
                "Either 'file' or 'text_content' must be provided."
            )
        return data

    class Meta:
        model = Document
        fields = (
            "external_id",
            "title",
            "created_at",
            "modified_at",
            "description",
            "document_type",
            "file",
            "text_content",
        )
        read_only_fields = ("external_id", "created_at", "modified_at")


class DocumentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = (
            "title",
            "description",
        )
