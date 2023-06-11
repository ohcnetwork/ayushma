from rest_framework import status

from ayushma.tests.test_base import TestBase

# TODO: Write more better test. Currently only checking the authorization


class TestDocument(TestBase):
    def setUp(self) -> None:
        super(TestDocument, self).setUp()

        # Testing with unauthorized user
        self.client.login(email=self.user.email, password="testing123")

    def test_create_document(self):
        """Testing create document API"""
        data = {
            "title": "Test Document",
            "description": "Test Description",
            "project": self.project,
        }
        response = self.client.post(
            f"/api/projects/{self.project.external_id}/documents",
            data=data,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_document(self):
        """Testing get document API"""
        response = self.client.get(
            f"/api/projects/{self.project.external_id}/documents"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_document_detail(self):
        """Testing get document detail API"""
        response = self.client.get(
            f"/api/projects/{self.project.external_id}/documents/{self.document.external_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_document(self):
        """Testing update document API"""
        data = {"title": "Test Document"}
        response = self.client.patch(
            f"/api/projects/{self.project.external_id}/documents/{self.document.external_id}",
            data=data,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
