import uuid

from rest_framework import serializers

from ayushma.models import Document
from ayushma.utils.upload_file import upload_file


class DocumentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=False)

    def validate(self, data):
        if "file" not in data and "text_content" not in data:
            raise serializers.ValidationError(
                "Either 'file' or 'text_content' must be provided."
            )

        return super().validate(data)

    def save(self, **kwargs):
        if "file" in self.validated_data:
            doc_file = self.validated_data.pop("file")
            file_name, file_extension = doc_file.name.split(".")
            s3_url = upload_file(
                file=doc_file,
                s3_key=f"{file_name}_{uuid.uuid4()}.{file_extension}",
            )
            if not s3_url:
                raise serializers.ValidationError("File upload failed.")
            self.validated_data["s3_url"] = s3_url
        return super().save(**kwargs)

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
