from rest_framework import status
from rest_framework.authtoken.models import Token

from ayushma.models.token import ResetPasswordToken
from ayushma.models.users import User
from ayushma.tests.test_base import TestBase


class TestAuth(TestBase):
    def test_register(self):
        """Testing the register API"""

        # Testing with duplicate fields
        response = self.client.post(
            "/api/auth/register",
            {
                "username": self.user.username,
                "full_name": self.user.full_name,
                "email": self.user.email,
                "password": self.user.password,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()["username"][0],
            "A user with that username already exists.",
        )
        self.assertEqual(
            response.json()["email"][0],
            "user with this email address already exists.",
        )

        # Testing with missing fields
        response = self.client.post(
            "/api/auth/register",
            {
                "username": "test",
                "full_name": "test",
                "email": "test@g.com",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["password"][0], "This field is required.")

        # Testing with valid data
        response = self.client.post(
            "/api/auth/register",
            {
                "username": "test",
                "full_name": "test",
                "email": "test@g.com",
                "password": "test@123",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="test").exists())

    def test_login(self):
        """Testing the login API"""

        # Testing with missing fields
        response = self.client.post(
            "/api/auth/login",
            {"email": self.user.email},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["password"][0], "This field is required.")

        # Testing with invalid credentials
        response = self.client.post(
            "/api/auth/login",
            {"email": "wrong@g.com", "password": "wrongpassword"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()["non_field_errors"][0],
            "Unable to log in with provided credentials.",
        )

        # Testing with valid credentials
        response = self.client.post(
            "/api/auth/login",
            {
                "email": "testing@g.com",
                "password": "testing123",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["token"], Token.objects.get(user=self.user).key)

    def test_logout(self):
        """Testing the logout API"""

        # Testing with unauthenticated user
        response = self.client.delete("/api/auth/logout")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "No auth token provided",
        )

        # Testing with authenticated user
        self.client.force_login(user=self.user)
        token = Token.objects.create(user=self.user)
        response = self.client.delete(
            "/api/auth/logout", **{"HTTP_AUTHORIZATION": f"Token {token.key}"}
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Token.objects.filter(key=token.key).exists())

    def test_forgot_password(self):
        """Testing the forgot password API"""

        # Testing with missing fields
        response = self.client.post("/api/auth/forgot")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["email"][0], "This field is required.")

        # Testing with wrong data
        response = self.client.post(
            "/api/auth/forgot",
            {"email": "wrong@g.com"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Testing with inactive user
        user = self.create_user(username="test1", email="test1@g.com")
        user.is_active = False
        user.save()
        response = self.client.post(
            "/api/auth/forgot",
            {"email": user.email},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "This account is inactive. Please contact admin.",
        )
        User.objects.filter(username="test1").delete()

        # Testing with valid data
        response = self.client.post(
            "/api/auth/forgot",
            {"email": self.user.email},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(ResetPasswordToken.objects.filter(user=self.user).exists())

    def test_verify_token(self):
        """Testing the verify token API"""

        # Testing with missing fields
        response = self.client.post("/api/auth/verify")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["email"][0], "This field is required.")
        self.assertEqual(response.json()["token"][0], "This field is required.")

        # Testing with wrong data
        response = self.client.post(
            "/api/auth/verify",
            {"token": "wrongtoken", "email": "wrong@g.com"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()["token"][0],
            "The OTP password entered is not valid. Please check and try again.",
        )

        # Testing with other token
        user = self.create_user(username="test1", email="test1@g.com")
        token = self.create_reset_password_token(user=user)
        response = self.client.post(
            "/api/auth/verify",
            {"token": token.key, "email": self.user.email},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()["token"][0],
            "The OTP password entered is not valid. Please check and try again.",
        )

        # Testing with inactive user
        user.is_active = False
        user.save()
        response = self.client.post(
            "/api/auth/verify",
            {"token": token.key, "email": user.email},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()["detail"][0],
            "This account is inactive. Please contact admin.",
        )

        # Testing with expired token
        token = self.create_reset_password_token(user=self.user, expired=True)
        response = self.client.post(
            "/api/auth/verify",
            {"token": token.key, "email": self.user.email},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()["token"][0],
            "The OTP password has expired. Please try again.",
        )
        ResetPasswordToken.objects.filter(user=self.user).delete()

        # Testing with valid token
        token = self.create_reset_password_token(user=self.user)
        response = self.client.post(
            "/api/auth/verify",
            {"token": token.key, "email": self.user.email},
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data["username"], self.user.username)

    def test_reset_password_with_token(self):
        """Testing the reset password API with token"""

        # Testing with missing fields
        response = self.client.post("/api/auth/reset")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["email"][0], "This field is required.")
        self.assertEqual(response.json()["token"][0], "This field is required.")
        self.assertEqual(response.json()["password"][0], "This field is required.")

        # Testing with wrong data
        response = self.client.post(
            "/api/auth/reset",
            {
                "email": "wrong@gmail.com",
                "token": "wrongtoken",
                "password": "test@123",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()["token"][0],
            "The OTP password entered is not valid. Please check and try again.",
        )

        # Testing with other token
        user = self.create_user(username="test1", email="test1@g.com")
        token = self.create_reset_password_token(user=user)
        response = self.client.post(
            "/api/auth/verify",
            {
                "token": token.key,
                "email": self.user.email,
                "password": "test@123",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["token"][0],
            "The OTP password entered is not valid. Please check and try again.",
        )

        # Testing with inactive user
        user.is_active = False
        user.save()
        response = self.client.post(
            "/api/auth/verify",
            {
                "token": token.key,
                "email": user.email,
                "password": "test@123",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()["detail"][0],
            "This account is inactive. Please contact admin.",
        )

        # Testing with expired token
        token = self.create_reset_password_token(user=self.user, expired=True)
        response = self.client.post(
            "/api/auth/reset",
            {
                "email": self.user.email,
                "token": token.key,
                "password": "test@123",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["token"][0],
            "The OTP password has expired. Please try again.",
        )
        ResetPasswordToken.objects.filter(user=self.user).delete()

        # Testing with valid token
        token = self.create_reset_password_token(user=self.user)
        response = self.client.post(
            "/api/auth/reset",
            {
                "email": self.user.email,
                "token": token.key,
                "password": "test@123",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_reset_password_without_token(self):
        """Testing the reset password API without token"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/api/auth/reset",
            {
                "email": self.user.email,
                "password": "test@123",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.client.logout()
