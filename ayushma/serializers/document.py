import os
import uuid

from django.conf import settings
from django.core.files.storage import FileSystemStorage
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
            full_file_name = f"{file_name}_{uuid.uuid4()}.{file_extension}"
            s3_url = upload_file(
                file=doc_file,
                s3_key=full_file_name,
            )
            if not s3_url:
                # saves file to media folder
                folder = os.path.join(settings.MEDIA_ROOT, "documents")
                try:
                    os.mkdir(folder)
                except:
                    pass

                fs = FileSystemStorage(location=folder)
                fs.save(full_file_name, doc_file)

                s3_url = full_file_name

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
            "s3_url",
            "text_content",
        )
        read_only_fields = ("external_id", "created_at", "s3_url", "modified_at")


class DocumentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = (
            "title",
            "description",
        )
