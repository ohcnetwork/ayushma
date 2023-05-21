from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from ayushma.models import Document, DocumentType, Project
from ayushma.serializers.document import DocumentSerializer, DocumentUpdateSerializer
from ayushma.utils.upsert import upsert
from utils.views.base import BaseModelViewSet


@extend_schema_view(
    destroy=extend_schema(exclude=True),
    partial_update=extend_schema(exclude=False),
    create=extend_schema(exclude=False),
    retrieve=extend_schema(
        description="Get Documents",
    ),
)
class DocumentViewSet(BaseModelViewSet):
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
        document = serializer.save(project=project)

        try:
            if document.document_type == DocumentType.FILE:
                upsert(external_id=external_id, s3_url=str(document.s3_url))
            elif document.document_type == DocumentType.URL:
                upsert(external_id=external_id, url=document.text_content)
            elif document.document_type == DocumentType.TEXT:
                upsert(external_id=external_id, text=document.text_content)
            else:
                raise Exception("Invalid document type.")
        except Exception as e:
            return Response({"non_field_errors": str(e)}, status=400)
