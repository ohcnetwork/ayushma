from django.conf import settings
from django.urls import include, path
from rest_framework_nested import routers

from .views.auth import APILoginView, APILogoutView
from .views.chat import ChatViewSet
from .views.users import UserViewSet

app_name = "api"

router = routers.SimpleRouter(trailing_slash=False)
NestedRouter = routers.NestedSimpleRouter
if settings.DEBUG:
    router = routers.DefaultRouter(trailing_slash=False)
    NestedRouter = routers.NestedDefaultRouter


router.register(r"users", UserViewSet)

auth_urls = [
    path("login", APILoginView.as_view(), name="login"),
    path("logout", APILogoutView.as_view(), name="logout"),
]

urlpatterns = [
    path(r"", include(router.urls)),
    path("auth/", include(auth_urls)),
    path("chat", ChatViewSet.as_view()),
]
