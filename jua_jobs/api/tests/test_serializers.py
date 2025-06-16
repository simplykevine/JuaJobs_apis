from django.test import TestCase
from api.models import User, JobPosting, Application, Review
from api.serializers import (
    UserSignupSerializer,
    UserLoginSerializer,
    JobPostingSerializer,
    ApplicationSerializer,
    ReviewSerializer
)
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone


class UserSerializerTests(TestCase):
    def test_user_signup_serializer_valid(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }
        serializer = UserSignupSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("testpass123"))

    def test_user_login_serializer_valid(self):
        user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        data = {"email": "test@example.com", "password": "testpass123"}
        serializer = UserLoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["user"], user)

    def test_user_login_serializer_invalid(self):
        data = {"email": "invalid@example.com", "password": "wrongpass"}
        serializer = UserLoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class JobPostingSerializerTests(TestCase):
    def setUp(self):
        self.poster = User.objects.create_user(username="poster", email="poster@example.com", password="pass123")
        self.worker = User.objects.create_user(username="worker", email="worker@example.com", password="pass123")
        self.job = JobPosting.objects.create(title="Test Job", description="Details", posted_by=self.poster)
        self.application = Application.objects.create(
            job=self.job,
            worker=self.worker,
            cover_letter=SimpleUploadedFile("cover.pdf", b"hello", content_type="application/pdf")
        )

    def test_job_posting_serializer_includes_applicants(self):
        serializer = JobPostingSerializer(instance=self.job)
        self.assertIn("applicants", serializer.data)
        self.assertEqual(len(serializer.data["applicants"]), 1)
        self.assertEqual(serializer.data["applicants"][0]["worker_email"], self.worker.email)


class ApplicationSerializerTests(TestCase):
    def setUp(self):
        self.worker = User.objects.create_user(username="worker", email="worker@example.com", password="pass123")
        self.poster = User.objects.create_user(username="poster", email="poster@example.com", password="pass123")
        self.job = JobPosting.objects.create(title="A Job", description="Description", posted_by=self.poster)

    def test_application_serializer_valid(self):
        fake_file = SimpleUploadedFile("cv.pdf", b"content", content_type="application/pdf")
        data = {
            "job": self.job.id,
            "cover_letter": fake_file
        }
        serializer = ApplicationSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class ReviewSerializerTests(TestCase):
    def setUp(self):
        self.reviewer = User.objects.create_user(username="rev1", email="rev1@example.com", password="pass")
        self.reviewee = User.objects.create_user(username="rev2", email="rev2@example.com", password="pass")
        self.job = JobPosting.objects.create(title="Reviewed Job", description="...", posted_by=self.reviewer)

    def test_review_serializer_valid(self):
        data = {
            "reviewer": self.reviewer.id,
            "reviewee": self.reviewee.id,
            "job": self.job.id,
            "rating": 5,
            "comment": "Good work",
            "created_at": timezone.now()
        }
        serializer = ReviewSerializer(data=data)
        self.assertTrue(serializer.is_valid())
