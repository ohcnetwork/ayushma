from uuid import uuid4

from django.test.client import BOUNDARY, MULTIPART_CONTENT, encode_multipart
from rest_framework import status
from rest_framework.exceptions import APIException

from ayushma.models.chat import Chat
from ayushma.tests.test_base import TestBase

# TODO: Add tests for converse API


class TestChat(TestBase):
    @classmethod
    def setUpTestData(cls):
        super(TestChat, cls).setUpTestData()
        cls.create_chat(cls.superuser, cls.project, cls.api_key)

    def setUp(self) -> None:
        super(TestChat, self).setUp()
        self.client.login(email=self.user.email, password="testing123")

    def test_create_chat(self):
        """Testing create chat API"""

        # Testing with missing fields
        response = self.client.post(f"/api/projects/{self.project.external_id}/chats")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["title"][0], "This field is required.")

        data = {"title": "Test Message"}

        # Testing with invalid project id
        project_tmp_id = uuid4()
        response = self.client.post(
            f"/api/projects/{project_tmp_id}/chats",
            data=data,
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Testing with valid data
        response = self.client.post(
            f"/api/projects/{self.project.external_id}/chats",
            data=data,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], data["title"])
        self.assertTrue(Chat.objects.filter(title=data["title"]).exists())

        user = self.create_user(username="test_user", email="test@g.com")
        self.client.force_login(user)

        # Testing with no key
        response = self.client.post(
            f"/api/projects/{self.project.external_id}/chats",
            data=data,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["error"],
            "OpenAI-Key header is required to create a chat",
        )

        # Testing with key
        response = self.client.post(
            f"/api/projects/{self.project.external_id}/chats",
            data=data,
            HTTP_OpenAI_Key=uuid4(),
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], data["title"])

    def test_get_chat(self):
        """Testing get chat API"""

        # Testing with invalid project id
        project_tmp_id = uuid4()
        response = self.client.get(f"/api/projects/{project_tmp_id}/chats")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

        # Testing with valid data
        response = self.client.get(f"/api/projects/{self.project.external_id}/chats")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_get_chat_detail(self):
        """Testing get chat detail API"""

        # Testing with invalid project id
        project_tmp_id = uuid4()
        response = self.client.get(
            f"/api/projects/{project_tmp_id}/chats/{self.chat.external_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Testing with invalid chat id
        chat_tmp_id = uuid4()
        response = self.client.get(
            f"/api/projects/{self.project.external_id}/chats/{chat_tmp_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Testing with valid data
        response = self.client.get(
            f"/api/projects/{self.project.external_id}/chats/{self.chat.external_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.chat.title)

    def test_update_chat(self):
        """Testing update chat API"""

        # Testing with invalid project id
        project_tmp_id = uuid4()
        response = self.client.patch(
            f"/api/projects/{project_tmp_id}/chats/{self.chat.external_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Testing with invalid chat id
        chat_tmp_id = uuid4()
        response = self.client.patch(
            f"/api/projects/{self.project.external_id}/chats/{chat_tmp_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Testing with valid data
        data = {
            "title": "Update Message",
        }
        response = self.client.patch(
            f"/api/projects/{self.project.external_id}/chats/{self.chat.external_id}",
            data=data,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], data["title"])
        self.assertTrue(Chat.objects.filter(title=data["title"]).exists())

    def test_list_all_chats(self):
        """Testing list all chats API"""

        self.client.force_login(self.superuser)

        # Testing with invalid project id
        project_tmp_id = uuid4()
        response = self.client.get(f"/api/projects/{project_tmp_id}/chats/list_all")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

        # Testing with valid data
        response = self.client.get(
            f"/api/projects/{self.project.external_id}/chats/list_all"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(len(response.data[0]["chats"]), 1)
        self.assertEqual(
            response.data[0]["chats"][0]["message"],
            self.chat_message.message,
        )


class TestConverse(TestBase):
    def request(self, data={}, api_key: str = None, key: str = None):
        return self.client.post(
            f"/api/projects/{self.project.external_id}/chats/{self.chat.external_id}/converse",
            data=encode_multipart(boundary=BOUNDARY, data=data),
            HTTP_X_API_KEY=api_key,
            HTTP_OpenAI_Key=key,
            content_type=MULTIPART_CONTENT,
        )

    def test_converse(self):
        """Testing converse API"""

        data = dict(text="Hello", stream="false")

        # Testing with no authentication
        response = self.request(data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"],
            "Authentication credentials were not provided.",
        )

        # Testing with authenticated user with no openai key
        user = self.create_user(username="test_user", email="test1@g.com")
        self.client.force_login(user)
        response = self.request(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["error"],
            "OpenAI-Key header is required to create a chat",
        )

        self.client.force_login(self.user)

        # Testing with missing fields
        response = self.request(data=dict())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["error"],
            "Please provide text to generate transcript",
        )

        # Testing with translation failed
        response = self.request(
            data=dict(text="Hello", language="hi"),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertRaises(expected_exception=APIException)

        response = self.request(data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
