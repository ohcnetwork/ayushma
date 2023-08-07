import json

from django.conf import settings
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from ayushma.models import Document, DocumentType, Project
from ayushma.serializers.document import DocumentSerializer, DocumentUpdateSerializer
from ayushma.utils.upsert import upsert
from utils.views.base import BaseModelViewSet
from utils.views.mixins import PartialUpdateModelMixin


class DocumentViewSet(
    BaseModelViewSet,
    PartialUpdateModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    ListModelMixin,
):
    queryset = Document.objects.all()
    serializer_action_classes = {
        "list": DocumentSerializer,
        "retrieve": DocumentSerializer,
        "create": DocumentSerializer,
        "update": DocumentUpdateSerializer,
        "partial_update": DocumentUpdateSerializer,
    }
    permission_classes = (IsAdminUser,)
    parser_classes = (MultiPartParser,)
    lookup_field = "external_id"

    def get_queryset(self):
        queryset = self.queryset.filter(
            project__external_id=self.kwargs["project_external_id"]
        )
        return queryset

    def perform_create(self, serializer):
        external_id = self.kwargs["project_external_id"]
        project = Project.objects.get(external_id=external_id)

        if project.archived:
            raise ValidationError(
                {"non_field_errors": "Project is archived. Cannot add documents."}
            )

        document = serializer.save(project=project)

        try:
            if document.document_type == DocumentType.FILE:
                upsert(
                    external_id=external_id,
                    s3_url=self.request.build_absolute_uri(document.file.url),
                    document_id=document.external_id,
                )
            elif document.document_type == DocumentType.URL:
                upsert(
                    external_id=external_id,
                    url=document.text_content,
                    document_id=document.external_id,
                )
            elif document.document_type == DocumentType.TEXT:
                upsert(
                    external_id=external_id,
                    text=document.text_content,
                    document_id=document.external_id,
                )
            else:
                raise Exception("Invalid document type.")
        except Exception as e:
            raise ValidationError({"non_field_errors": str(e)})

    def perform_destroy(self, instance):
        # delete namespace from vectorDB
        try:
            settings.PINECONE_INDEX_INSTANCE.delete(
                namespace=self.kwargs["project_external_id"],
                filter={"document": str(instance.external_id)},
            )
        except Exception as e:
            print(e)
            return Response(
                {"non_field_errors": "Error deleting document from vectorDB"},
                status=400,
            )
        return super().perform_destroy(instance)
