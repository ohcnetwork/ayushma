from django.conf import settings
from django.urls import include, path
from rest_framework_nested import routers

from ayushma.views.auth import AuthViewSet
from ayushma.views.chat import ChatFeedbackViewSet, ChatViewSet
from ayushma.views.document import ProjectDocumentViewSet, TestQuestionDocumentViewSet
from ayushma.views.orphan import OrphanChatViewSet
from ayushma.views.project import ProjectViewSet
from ayushma.views.service import TempTokenViewSet
from ayushma.views.testsuite import (
    FeedbackViewSet,
    TestQuestionViewSet,
    TestRunViewSet,
    TestSuiteViewSet,
)
from ayushma.views.token import ResetPasswordViewset
from ayushma.views.users import UserViewSet

app_name = "api"

router = routers.SimpleRouter(trailing_slash=False)
NestedRouter = routers.NestedSimpleRouter
if settings.DEBUG:
    router = routers.DefaultRouter(trailing_slash=False)
    NestedRouter = routers.NestedDefaultRouter


router.register(r"users", UserViewSet)
router.register(r"auth", ResetPasswordViewset, basename="token")
router.register(r"auth", AuthViewSet, basename="auth")
router.register(r"chats", OrphanChatViewSet, basename="orphan_chat")
router.register(r"feedback", ChatFeedbackViewSet, basename="feedback")
router.register(r"temptokens", TempTokenViewSet, basename="temptoken")

router.register(r"projects", ProjectViewSet)
projects_router = NestedRouter(router, r"projects", lookup="project")
projects_router.register(r"documents", ProjectDocumentViewSet)
projects_router.register(r"chats", ChatViewSet)

router.register(r"tests/suites", TestSuiteViewSet)
tests_router = NestedRouter(router, r"tests/suites", lookup="test_suite")
tests_router.register(r"questions", TestQuestionViewSet)
test_question_router = NestedRouter(tests_router, r"questions", lookup="test_question")
test_question_router.register(r"documents", TestQuestionDocumentViewSet)
tests_router.register(r"runs", TestRunViewSet)
runs_router = NestedRouter(tests_router, r"runs", lookup="run")
runs_router.register(r"feedback", FeedbackViewSet)

urlpatterns = [
    path(r"", include(router.urls)),
    path(r"", include(projects_router.urls)),
    path(r"", include(tests_router.urls)),
    path(r"", include(test_question_router.urls)),
    path(r"", include(runs_router.urls)),
]
