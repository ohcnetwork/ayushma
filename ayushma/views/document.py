from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAdminUser

from ayushma.models import Document, Project
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
        # upsert file
        upsert(filepath=str(document.file), external_id=external_id)
