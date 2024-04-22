from rest_framework import serializers

from ayushma.models import Document


class DocumentSerializer(serializers.ModelSerializer):
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
            "uploading",
        )
        read_only_fields = (
            "external_id",
            "created_at",
            "modified_at",
            "uploading",
        )
        write_only_fields = ("file",)

    def validate(self, data):
        if "file" not in data and "text_content" not in data:
            raise serializers.ValidationError(
                "Either 'file' or 'text_content' must be provided."
            )

        return super().validate(data)


class DocumentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = (
            "title",
            "description",
        )
