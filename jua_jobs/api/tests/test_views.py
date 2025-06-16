from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from api.models import User, JobPosting, Application, Review
from django.core.files.uploadedfile import SimpleUploadedFile

class UserAuthTests(APITestCase):
    def setUp(self):
        self.signup_url = reverse('signup')
        self.login_url = reverse('login')

    def test_user_signup(self):
        response = self.client.post(self.signup_url, {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)

    def test_user_login(self):
        User.objects.create_user(email="login@example.com", username="loginuser", password="loginpass123")
        response = self.client.post(self.login_url, {
            "email": "login@example.com",
            "password": "loginpass123"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_token_protected_route(self):
        user = User.objects.create_user(email="secure@example.com", username="secure", password="secure123")
        login = self.client.post(self.login_url, {
            "email": "secure@example.com",
            "password": "secure123"
        })
        token = login.data["token"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get(reverse('test-token'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)


class JobPostingTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="poster@example.com", username="poster", password="pass123")
        self.client = APIClient()
        login = self.client.post(reverse('login'), {"email": "poster@example.com", "password": "pass123"})
        self.token = login.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_create_job_posting(self):
        response = self.client.post('/api/jobs/', {
            "title": "Test Job",
            "description": "Job Description"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Test Job")


class ApplicationTests(APITestCase):
    def setUp(self):
        self.worker = User.objects.create_user(email="worker@example.com", username="worker", password="pass123")
        self.poster = User.objects.create_user(email="poster@example.com", username="poster", password="pass123")
        self.job = JobPosting.objects.create(title="Dev Job", description="details", posted_by=self.poster)

        self.client = APIClient()
        login = self.client.post(reverse('login'), {"email": "worker@example.com", "password": "pass123"})
        self.token = login.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_create_application(self):
        fake_file = SimpleUploadedFile("cover.pdf", b"fake content", content_type="application/pdf")
        response = self.client.post('/api/applications/', {
            "job": self.job.id,
            "cover_letter": fake_file
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ReviewTests(APITestCase):
    def setUp(self):
        self.reviewer = User.objects.create_user(email="rev1@example.com", username="rev1", password="pass123")
        self.reviewee = User.objects.create_user(email="rev2@example.com", username="rev2", password="pass123")
        self.job = JobPosting.objects.create(title="Reviewed Job", description="desc", posted_by=self.reviewer)

        self.client = APIClient()
        login = self.client.post(reverse('login'), {"email": "rev1@example.com", "password": "pass123"})
        self.token = login.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_create_review(self):
        response = self.client.post('/api/reviews/', {
            "reviewer": self.reviewer.id,
            "reviewee": self.reviewee.id,
            "job": self.job.id,
            "rating": 5,
            "comment": "Excellent collaboration!"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
