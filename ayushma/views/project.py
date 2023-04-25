from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from ayushma.models import Project
from ayushma.serializers.project import ProjectSerializer


@extend_schema_view(
    destroy=extend_schema(exclude=True),
    partial_update=extend_schema(exclude=False),
    create=extend_schema(exclude=False),
    retrieve=extend_schema(
        description="Get Projects",
    ),
)
class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
