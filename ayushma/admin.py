from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from djangoql.admin import DjangoQLSearchMixin
from simple_history.admin import SimpleHistoryAdmin

from ayushma.models.services import Service, TempToken
from ayushma.models.testsuite import Feedback, TestQuestion, TestRun, TestSuite

from .models import APIKey, Chat, ChatMessage, Document, Project, User


@admin.register(User)
class UserAdmin(DjangoQLSearchMixin, BaseUserAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "full_name",
        "is_staff",
    )
    list_display_links = list_display
    filter_horizontal = (*BaseUserAdmin.filter_horizontal,)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )
    fieldsets = (
        (
            None,
            {"fields": ("email", "username", "password", "external_id", "allow_key")},
        ),
        (
            "User info",
            {
                "fields": (
                    "full_name",
                    "last_login_platform",
                    "last_login_ip",
                )
            },
        ),
        (
            "Important dates",
            {
                "fields": (
                    "last_login",
                    "modified_at",
                    "date_joined",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )
    readonly_fields = ("modified_at", "last_login", "date_joined")


@admin.register(Chat)
class ChatAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(ChatMessage)
class ChatMessageAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(Project)
class ProjectAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(Document)
class DocumentAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(APIKey)
class APIKeyAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(TempToken)
class TempTokenAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(Service)
class ServiceAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(Feedback)
class FeedbackAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(TestSuite)
class TestSuiteAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(TestQuestion)
class TestQuestionAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(TestRun)
class TestRunAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


admin.site.site_header = "Ayushma Admin"
