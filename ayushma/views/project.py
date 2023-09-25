from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from ayushma.models import Project
from ayushma.serializers.project import ProjectSerializer, ProjectUpdateSerializer
from utils.views.base import BaseModelViewSet
from utils.views.mixins import PartialUpdateModelMixin


class ProjectViewSet(
    BaseModelViewSet,
    PartialUpdateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
):
    queryset = Project.objects.all()
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    search_fields = ("title",)
    filterset_fields = ("archived",)
    serializer_class = ProjectSerializer
    permission_classes = (IsAdminUser,)
    permission_action_classes = {
        "list": (IsAuthenticated(),),
        "retrieve": (IsAuthenticated(),),
    }
    lookup_field = "external_id"

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return ProjectUpdateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "list":
            if not self.request.user.is_staff:
                queryset = self.queryset.filter(is_default=True)
        return queryset

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def perform_destroy(self, instance):
        # delete namespaces from vectorDB
        try:
            settings.PINECONE_INDEX_INSTANCE.delete(
                namespace=str(instance.external_id),
                deleteAll=True,
            )
        except Exception as e:
            print(e)
            return Response(
                {
                    "non_field_errors": "Error deleting documents from vectorDB for this project"
                },
                status=400,
            )
        return super().perform_destroy(instance)
