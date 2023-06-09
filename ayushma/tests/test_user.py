from rest_framework import status

from ayushma.models import User
from ayushma.tests.test_base import TestBase


class TestSuperUser(TestBase):
    def setUp(self) -> None:
        self.client.force_authenticate(user=self.superuser)

    def get_representation(self, user: User) -> dict:
        return {
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "allow_key": user.allow_key,
            "is_staff": user.is_staff,
        }

    def test_access_url_superuser(self):
        """Test super user can access the url by location"""
        response = self.client.get(f"/api/users/{self.superuser.username}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_superuser(self):
        """Testing the get user API"""
        response = self.client.get("/api/users/me")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res_data = response.json()
        res_data.pop("external_id")
        self.assertDictEqual(res_data, self.get_representation(self.superuser))

    def test_get_user_list(self):
        """Testing the get user list API"""
        response = self.client.get("/api/users")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_edit_superuser(self):
        """Testing the edit super user API"""
        username = self.superuser.username
        response = self.client.patch(
            f"/api/users/{username}",
            {"full_name": "Super User1"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["full_name"], "Super User1")
        self.assertEqual(User.objects.get(username=username).full_name, "Super User1")

    def test_delete_superuser(self):
        """Testing the delete super user API"""
        username = self.superuser.username
        response = self.client.delete(f"/api/users/{username}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(username=username).exists())


class TestUser(TestBase):
    @classmethod
    def setUpTestData(cls) -> None:
        super(TestUser, cls).setUpTestData()
        cls.user_2 = cls.create_user(username="testuser2", email="testing2@g.com")

    def setUp(self) -> None:
        self.client.force_login(user=self.user)

    def get_representation(self, user: User) -> dict:
        return {
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "allow_key": user.allow_key,
            "is_staff": user.is_staff,
        }

    def test_access_url_user(self):
        """Test user can't access the url by location"""
        response = self.client.get(f"/api/users/{self.user.username}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_url_other_user(self):
        """Test user can't read other user's data"""
        response = self.client.get(f"/api/users/{self.user_2.username}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_user(self):
        """Testing the get user API"""
        response = self.client.get("/api/users/me")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res_data = response.json()
        res_data.pop("external_id")
        self.assertDictEqual(res_data, self.get_representation(self.user))

    def test_get_user_list(self):
        """Testing the get user list API"""
        response = self.client.get("/api/users")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_edit_user(self):
        """Testing the edit user API"""
        response = self.client.patch(
            f"/api/users/{self.user.username}",
            {"full_name": "Test User1"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user(self):
        """Testing the delete user API"""
        username = self.user.username
        response = self.client.delete(f"/api/users/{username}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
