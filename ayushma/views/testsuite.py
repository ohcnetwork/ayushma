from rest_framework import filters
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from ayushma.models.project import Project
from ayushma.models.testsuite import (
    Feedback,
    TestQuestion,
    TestResult,
    TestRun,
    TestSuite,
)
from ayushma.serializers.testsuite import (
    FeedbackSerializer,
    TestQuestionSerializer,
    TestResultSerializer,
    TestRunSerializer,
    TestSuiteSerializer,
)
from ayushma.tasks.testrun import mark_test_run_as_completed
from utils.views.base import BaseModelViewSet


class IsStaffOrReviewer(IsAdminUser):
    def has_permission(self, request, view):
        return request.user.is_staff or request.user.is_reviewer


class TestSuiteViewSet(BaseModelViewSet):
    queryset = TestSuite.objects.all()
    permission_classes = [IsAuthenticated, IsStaffOrReviewer]
    serializer_class = TestSuiteSerializer

    lookup_field = "external_id"

    filter_backends = [filters.OrderingFilter]


class TestQuestionViewSet(BaseModelViewSet):
    queryset = TestQuestion.objects.all()
    permission_classes = [IsAuthenticated, IsStaffOrReviewer]
    serializer_class = TestQuestionSerializer

    lookup_field = "external_id"

    filter_backends = [filters.OrderingFilter]

    def get_queryset(self):
        queryset = self.queryset.filter(
            test_suite__external_id=self.kwargs["test_suite_external_id"]
        )
        return queryset

    def perform_create(self, serializer):
        external_id = self.kwargs["test_suite_external_id"]
        test_suite = TestSuite.objects.get(external_id=external_id)
        return serializer.save(test_suite=test_suite)


class TestRunViewSet(BaseModelViewSet):
    queryset = TestRun.objects.all()
    permission_classes = [IsAuthenticated, IsStaffOrReviewer]
    serializer_class = TestRunSerializer

    lookup_field = "external_id"

    filter_backends = [filters.OrderingFilter]

    def get_queryset(self):
        queryset = self.queryset.filter(
            test_suite__external_id=self.kwargs["test_suite_external_id"]
        )
        return queryset

    def perform_create(self, serializer):
        suite_external_id = self.kwargs["test_suite_external_id"]
        test_suite = TestSuite.objects.get(external_id=suite_external_id)

        project_external_id = serializer.validated_data["project"]["external_id"]
        project = Project.objects.get(external_id=project_external_id)

        test_run = serializer.save(test_suite=test_suite, project=project)

        mark_test_run_as_completed.delay(test_run.id)

        return test_run


class TestResultViewSet(BaseModelViewSet):
    queryset = TestResult.objects.all()
    permission_classes = [IsAuthenticated, IsStaffOrReviewer]
    serializer_class = TestResultSerializer


class FeedbackViewSet(BaseModelViewSet):
    queryset = Feedback.objects.all()
    permission_classes = [IsAuthenticated, IsStaffOrReviewer]
    serializer_class = FeedbackSerializer

    def get_queryset(self):
        test_result_id = self.request.query_params.get("test_result_id", None)
        if test_result_id is not None:
            queryset = self.queryset.filter(test_result__external_id=test_result_id)
        else:
            user = self.request.user
            if user.is_staff:
                queryset = self.queryset.all()
            else:
                queryset = self.queryset.filter(feedback__user=user)
        return queryset

    def perform_create(self, serializer):
        result_external_id = serializer.validated_data["test_result"]["external_id"]
        test_result = TestResult.objects.get(external_id=result_external_id)

        feedback = serializer.save(test_result=test_result, user=self.request.user)
        return feedback
