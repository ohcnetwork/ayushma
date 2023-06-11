from datetime import timedelta

from django.contrib.auth.hashers import make_password
from django.utils import timezone
from rest_framework.test import APITestCase

from ayushma.models.document import Document
from ayushma.models.project import Project
from ayushma.models.token import ResetPasswordToken
from ayushma.models.users import User

"""
Boilerplate code for tests
"""


class TestBase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        super(TestBase, cls).setUpTestData()
        cls.user = cls.create_user()
        cls.superuser = cls.create_super_user()
        cls.project = cls.create_project(cls.superuser, is_default=True)
        cls.document = cls.create_document(cls.project)

    @classmethod
    def create_user(
        cls,
        username: str = "testuser",
        full_name: str = "Test user",
        email: str = "testing@g.com",
        password: str = "testing123",
        **kwargs
    ) -> User:
        data = {
            "username": username,
            "full_name": full_name,
            "email": email,
            "password": make_password(password),
        }
        data.update(kwargs)
        return User.objects.create(**data)

    @classmethod
    def create_super_user(
        cls,
        username: str = "superuser",
        email: str = "superuser@g.com",
    ) -> User:
        user = cls.create_user(
            username=username,
            full_name="Super User",
            email=email,
            password="admin123",
        )
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user

    @classmethod
    def create_reset_password_token(
        cls, user: User, expired: bool = False
    ) -> ResetPasswordToken:
        token = ResetPasswordToken.objects.create(user=user)
        if expired:
            token.created_at = timezone.now() - timedelta(minutes=10)
            token.save()
        return token

    @classmethod
    def create_project(cls, user: User, is_default: bool = False, **kwargs) -> Project:
        data = {
            "title": "Test Project",
            "description": "Test Description",
            "prompt": "Test Prompt",
            "is_default": is_default,
        }
        data.update(kwargs)
        return Project.objects.create(creator=user, **data)

    @classmethod
    def create_document(cls, project: Project, **kwargs) -> Document:
        data = {
            "title": "Test Document",
            "description": "Test Description",
            "project": project,
        }
        data.update(kwargs)
        return Document.objects.create(**data)
