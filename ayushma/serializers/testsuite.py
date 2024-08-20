from rest_framework import serializers

from ayushma.models import (
    Document,
    Feedback,
    TestQuestion,
    TestResult,
    TestRun,
    TestSuite,
)
from ayushma.serializers.document import DocumentSerializer
from ayushma.serializers.project import ProjectUpdateSerializer
from ayushma.serializers.users import UserSerializer


class TestSuiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestSuite
        fields = (
            "name",
            "created_at",
            "modified_at",
            "temperature",
            "topk",
            "external_id",
        )

    read_only_fields = ("external_id", "created_at", "modified_at")


class TestQuestionSerializer(serializers.ModelSerializer):
    documents = DocumentSerializer(many=True, read_only=True)

    def get_documents(self, obj):
        documents = Document.objects.filter(test_question__external_id=obj.external_id)
        return DocumentSerializer(documents, many=True).data

    class Meta:
        model = TestQuestion
        fields = (
            "question",
            "language",
            "created_at",
            "modified_at",
            "human_answer",
            "external_id",
            "documents",
        )
        read_only_fields = ("external_id", "created_at", "modified_at")


class FeedbackSerializer(serializers.ModelSerializer):
    user_object = UserSerializer(source="user", read_only=True)
    test_result_id = serializers.CharField(
        write_only=True, required=True, source="test_result.external_id"
    )

    class Meta:
        model = Feedback
        fields = (
            "test_result_id",
            "user_object",
            "external_id",
            "rating",
            "notes",
            "created_at",
            "modified_at",
        )

        read_only_fields = (
            "user_object",
            "external_id",
            "created_at",
            "modified_at",
        )


class TestResultSerializer(serializers.ModelSerializer):
    feedback = FeedbackSerializer(source="feedback_set", many=True, read_only=True)
    references = DocumentSerializer(many=True, read_only=True)
    test_question = TestQuestionSerializer(read_only=True)

    class Meta:
        model = TestResult
        fields = "__all__"
        read_only_fields = (
            "external_id",
            "created_at",
            "modified_at",
            "test_run",
            "test_question",
            "references",
        )


class TestRunSerializer(serializers.ModelSerializer):
    project = serializers.UUIDField(source="project.external_id")
    project_object = ProjectUpdateSerializer(source="project", read_only=True)
    test_results = TestResultSerializer(
        source="testresult_set", many=True, read_only=True
    )

    class Meta:
        model = TestRun
        fields = (
            "external_id",
            "project",
            "project_object",
            "created_at",
            "modified_at",
            "status",
            "test_results",
            "references",
            "models",
        )
        read_only_fields = (
            "external_id",
            "created_at",
            "modified_at",
            "project",
            "test_results",
        )
