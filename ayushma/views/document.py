from rest_framework.exceptions import ValidationError
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from ayushma.models import Document, Project
from ayushma.models.testsuite import TestQuestion
from ayushma.serializers.document import DocumentSerializer, DocumentUpdateSerializer
from ayushma.tasks.upsertdoc import upsert_doc
from ayushma.utils.vectordb import VectorDB
from utils.views.base import BaseModelViewSet
from utils.views.mixins import PartialUpdateModelMixin

class ProjectDocumentViewSet(
    BaseModelViewSet,
    PartialUpdateModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
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

        doc_url = None
        try:
            doc_url = self.request.build_absolute_uri(document.file.url)
            # replace localhost with "django" (docker service name) for celery worker to access the file. This is a hack, feel free to improve.
            doc_url = doc_url.replace("http://localhost", "http://django")
        except Exception as e:
            print(e)
            pass


        upsert_doc.delay(document.external_id, doc_url)

    def perform_destroy(self, instance):
        # delete namespace from vectorDB
        
        try:
            VectorDB().delete_subject(
                partition_name=self.kwargs["project_external_id"].replace("-", "_"),
                subject=str(instance.external_id),
            )
            return super().perform_destroy(instance)
        except Exception as e:
            print(e)
            return Response(
                {"non_field_errors": "Error deleting document from vectorDB"},
                status=400,
            )


class TestQuestionDocumentViewSet(
    BaseModelViewSet,
    CreateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    ListModelMixin,
):
    queryset = Document.objects.all()
    serializer_action_classes = {
        "list": DocumentSerializer,
        "retrieve": DocumentSerializer,
        "create": DocumentSerializer,
    }
    permission_classes = (IsAdminUser,)
    parser_classes = (MultiPartParser,)
    lookup_field = "external_id"

    def get_queryset(self):
        queryset = self.queryset.filter(
            test_question__external_id=self.kwargs["test_question_external_id"]
        )
        return queryset

    def perform_create(self, serializer):
        external_id = self.kwargs["test_question_external_id"]
        test_question = TestQuestion.objects.get(external_id=external_id)

        document = serializer.save(test_question=test_question, uploading=False)
        test_question.documents.add(document)
        test_question.save()

        return document
