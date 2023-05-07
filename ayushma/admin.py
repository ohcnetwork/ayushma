from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from djangoql.admin import DjangoQLSearchMixin
from simple_history.admin import SimpleHistoryAdmin

from .models import Chat, ChatMessage, Document, Project, User


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
