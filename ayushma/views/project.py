from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from ayushma.models import Project
from ayushma.serializers.project import ProjectSerializer, ProjectUpdateSerializer
from utils.views.base import BaseModelViewSet


@extend_schema_view(
    destroy=extend_schema(exclude=True),
    partial_update=extend_schema(exclude=False),
    create=extend_schema(exclude=False),
    retrieve=extend_schema(
        description="Get Projects",
    ),
)
class ProjectViewSet(BaseModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (IsAdminUser,)
    serializer_action_classes = {
        "create": ProjectUpdateSerializer,
        "update": ProjectUpdateSerializer,
        "partial_update": ProjectUpdateSerializer,
    }
    permission_action_classes = {
        "list": (IsAuthenticated(),),
        "retrieve": (IsAuthenticated(),),
    }
    lookup_field = "external_id"

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "list":
            if not self.request.user.is_staff:
                queryset = self.queryset.filter(is_default=True)
        return queryset

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)
