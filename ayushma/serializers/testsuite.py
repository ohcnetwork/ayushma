from rest_framework import serializers

from ayushma.models import Feedback, TestQuestion, TestResult, TestRun, TestSuite
from ayushma.serializers.project import ProjectSerializer
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
    class Meta:
        model = TestQuestion
        fields = (
            "question",
            "language",
            "created_at",
            "modified_at",
            "human_answer",
            "external_id",
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

        read_only_fields = ("user_object", "external_id", "created_at", "modified_at")


class TestResultSerializer(serializers.ModelSerializer):
    feedback = FeedbackSerializer(source="feedback_set", many=True, read_only=True)

    class Meta:
        model = TestResult
        fields = "__all__"
        read_only_fields = (
            "external_id",
            "created_at",
            "modified_at",
            "test_run",
            "test_question",
        )


class TestRunSerializer(serializers.ModelSerializer):
    project = serializers.UUIDField(source="project.external_id")
    project_object = ProjectSerializer(source="project", read_only=True)
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
            "complete",
            "test_results",
        )
        read_only_fields = (
            "external_id",
            "created_at",
            "modified_at",
            "project",
            "complete",
            "test_results",
        )
