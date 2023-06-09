from rest_framework.test import APITestCase

from ayushma.models import User

"""
Boilerplate code for tests
"""


class TestBase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        super(APITestCase, cls).setUpTestData()
        cls.user = cls.create_user()
        cls.superuser = cls.create_super_user()

    @classmethod
    def create_user(
        cls,
        username: str = "testuser",
        full_name: str = "Test user",
        email: str = "testing@g.com",
        password: str = "testing123",
        **kwargs
    ):
        data = {
            "username": username,
            "full_name": full_name,
            "email": email,
            "password": password,
        }
        data.update(kwargs)
        return User.objects.create(**data)

    @classmethod
    def create_super_user(cls, username: str = "superuser"):
        user = cls.create_user(
            username=username,
            full_name="Super User",
            email="admin@g.com",
            password="admin123",
        )
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user
