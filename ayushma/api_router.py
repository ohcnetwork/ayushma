from django.conf import settings
from django.urls import include, path
from rest_framework_nested import routers

from ayushma.views.auth import AuthViewSet
from ayushma.views.chat import ChatViewSet
from ayushma.views.document import DocumentViewSet
from ayushma.views.orphan import OrphanChatViewSet
from ayushma.views.project import ProjectViewSet
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

router.register(r"projects", ProjectViewSet)
projects_router = NestedRouter(router, r"projects", lookup="project")
projects_router.register(r"documents", DocumentViewSet)
projects_router.register(r"chats", ChatViewSet)

urlpatterns = [
    path(r"", include(router.urls)),
    path(r"", include(projects_router.urls)),
]
