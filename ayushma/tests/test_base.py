from datetime import timedelta

from django.contrib.auth.hashers import make_password
from django.utils import timezone
from rest_framework.test import APITestCase

from ayushma.models.apikeys import APIKey
from ayushma.models.chat import Chat, ChatMessage
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
        cls.user = cls.create_user(allow_key=True)
        cls.superuser = cls.create_super_user(allow_key=True)
        cls.project = cls.create_project(cls.superuser, is_default=True)
        cls.document = cls.create_document(cls.project)
        cls.api_key = cls.create_api_key(cls.user)
        cls.chat = cls.create_chat(cls.user, cls.project, cls.api_key)
        cls.chat_message = cls.create_chat_message(cls.chat)

    @classmethod
    def create_user(
        cls,
        username: str = "testuser",
        full_name: str = "Test user",
        email: str = "testing@g.com",
        password: str = "testing123",
        allow_key: bool = False,
        **kwargs
    ) -> User:
        data = {
            "username": username,
            "full_name": full_name,
            "email": email,
            "password": make_password(password),
            "allow_key": allow_key,
        }
        data.update(kwargs)
        return User.objects.create(**data)

    @classmethod
    def create_super_user(
        cls,
        username: str = "superuser",
        email: str = "superuser@g.com",
        allow_key: bool = False,
    ) -> User:
        user = cls.create_user(
            username=username,
            full_name="Super User",
            email=email,
            password="admin123",
            allow_key=allow_key,
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
            token.created_at = timezone.now() - timedelta(minutes=11)
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

    @classmethod
    def create_api_key(cls, user: User, **kwargs) -> APIKey:
        data = {
            "title": "Test API Key",
            "key": "test_api_key",
            "creator": user,
        }
        data.update(kwargs)
        return APIKey.objects.create(**data)

    @classmethod
    def create_chat(cls, user: User, project: Project, key: APIKey, **kwargs) -> Chat:
        data = {
            "title": "Test Chat",
            "user": user,
            "project": project,
            "prompt": "Test Prompt",
            "api_key": key,
        }
        data.update(kwargs)
        return Chat.objects.create(**data)

    @classmethod
    def create_chat_message(
        cls,
        chat: Chat,
        message: str = "Test Message",
        messageType: int = 1,
        temperature: float = 0.5,
        top_k: int = 10,
        meta: dict = {},
        **kwargs
    ) -> ChatMessage:
        data = {
            "chat": chat,
            "messageType": messageType,
            "message": message,
            "original_message": message,
            "language": "en",
            "ayushma_audio_url": "https://test.com",
            "temperature": temperature,
            "top_k": top_k,
            "meta": meta,
        }
        data.update(kwargs)
        return ChatMessage.objects.create(**data)
