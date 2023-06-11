from rest_framework import status

from ayushma.tests.test_base import TestBase


class TestProject(TestBase):
    def test_create_project(self):
        """Testing create project API"""

        # Testing with unauthorized user
        self.client.login(email=self.user.email, password="testing123")

        data = {
            "title": "test_project",
            "description": "test description",
            "prompt": "test prompt",
        }
        response = self.client.post("/api/projects", data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.logout()

        # Testing with authorized user
        self.client.login(email=self.superuser.email, password="admin123")

        # Testing with missing data
        response = self.client.post("/api/projects")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["title"][0], "This field is required.")

        # Testing with valid data
        response = self.client.post("/api/projects", data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], data["title"])

    def test_get_project(self):
        """Testing get project API"""

        self.client.login(email=self.user.email, password="testing123")

        # Testing with is_default=True
        response = self.client.get("/api/projects")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

        # Testing with is_default=False
        self.create_project(self.superuser)
        response = self.client.get("/api/projects")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_get_project_detail(self):
        """Testing get project detail API"""

        self.client.login(email=self.user.email, password="testing123")

        # Testing with invalid project id
        response = self.client.get("/api/projects/123")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Not found.")

        # Testing with valid project id
        response = self.client.get(f"/api/projects/{self.project.external_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.project.title)

    def test_update_project(self):
        """Testing update project API"""

        # Testing with unauthorized user
        self.client.login(email=self.user.email, password="testing123")

        # NOTE: Default Project title is getting updated
        data = {"title": "updated title"}
        response = self.client.patch(
            f"/api/projects/{self.project.external_id}",
            data=data,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.logout()

        # Testing with authorized user
        self.client.login(email=self.superuser.email, password="admin123")

        # Testing with invalid project id
        response = self.client.patch("/api/projects/123", data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Not found.")

        # Testing with valid data
        response = self.client.patch(
            f"/api/projects/{self.project.external_id}",
            data=data,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], data["title"])

    def test_delete_project(self):
        """Testing delete project API"""

        # Testing with unauthorized user
        self.client.login(email=self.user.email, password="testing123")

        response = self.client.delete(f"/api/projects/{self.project.external_id}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.logout()

        # Testing with authorized user
        self.client.login(email=self.superuser.email, password="admin123")

        # Testing with invalid project id
        response = self.client.delete("/api/projects/123")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Not found.")

        # Testing with valid data
        response = self.client.delete(f"/api/projects/{self.project.external_id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
