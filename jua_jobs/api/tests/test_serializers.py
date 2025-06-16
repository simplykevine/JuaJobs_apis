from django.test import TestCase
from rest_framework.test import APIRequestFactory
from api.models import User, JobPosting, Application, Review, WorkerProfile, Skill, Category
from api.serializers import (
    UserSignupSerializer, UserLoginSerializer, JobPostingSerializer,
    ApplicationSerializer, ReviewSerializer, WorkerProfileSerializer
)
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

class UserSerializerTests(TestCase):
    
    def test_user_signup_serializer_valid(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "password_confirm": "testpass123",
            "role": "worker"
        }
        serializer = UserSignupSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("testpass123"))

    def test_user_signup_password_mismatch(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "password_confirm": "differentpass",
            "role": "worker"
        }
        serializer = UserSignupSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("Passwords don't match", str(serializer.errors))

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
        self.poster = User.objects.create_user(username="poster", email="poster@example.com", password="pass123", role="client")
        self.worker = User.objects.create_user(username="worker", email="worker@example.com", password="pass123", role="worker")
        self.category = Category.objects.create(name="Technology")
        self.skill = Skill.objects.create(name="Python")
        self.job = JobPosting.objects.create(
            title="Test Job", 
            description="Test description", 
            posted_by=self.poster,
            category=self.category
        )
        self.job.required_skills.add(self.skill)

    def test_job_posting_serializer_includes_applicants(self):
        # Create an application
        fake_file = SimpleUploadedFile("cover.pdf", b"content", content_type="application/pdf")
        application = Application.objects.create(
            job=self.job,
            worker=self.worker,
            cover_letter=fake_file
        )
        
        # Create request context with job owner
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = self.poster
        
        serializer = JobPostingSerializer(instance=self.job, context={'request': request})
        self.assertIn("applicants", serializer.data)
        self.assertEqual(len(serializer.data["applicants"]), 1)
        self.assertEqual(serializer.data["applicants"][0]["worker_email"], self.worker.email)

    def test_job_posting_create_with_skills(self):
        data = {
            "title": "New Job",
            "description": "Job description",
            "category_id": self.category.id,
            "skill_ids": [self.skill.id]
        }
        serializer = JobPostingSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        job = serializer.save(posted_by=self.poster)
        self.assertEqual(job.title, "New Job")
        self.assertEqual(job.category, self.category)
        self.assertIn(self.skill, job.required_skills.all())

class ApplicationSerializerTests(TestCase):
    
    def setUp(self):
        self.worker = User.objects.create_user(username="worker", email="worker@example.com", password="pass123", role="worker")
        self.poster = User.objects.create_user(username="poster", email="poster@example.com", password="pass123", role="client")
        self.job = JobPosting.objects.create(title="A Job", description="Description", posted_by=self.poster, status="active")

    def test_application_serializer_valid(self):
        fake_file = SimpleUploadedFile("cv.pdf", b"content", content_type="application/pdf")
        data = {
            "job_id": self.job.id,
            "cover_letter": fake_file
        }
        
        factory = APIRequestFactory()
        request = factory.post('/')
        request.user = self.worker
        
        serializer = ApplicationSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())

    def test_application_to_own_job_invalid(self):
        fake_file = SimpleUploadedFile("cv.pdf", b"content", content_type="application/pdf")
        data = {
            "job_id": self.job.id,
            "cover_letter": fake_file
        }
        
        factory = APIRequestFactory()
        request = factory.post('/')
        request.user = self.poster  # Job owner trying to apply
        
        serializer = ApplicationSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn("Cannot apply to your own job", str(serializer.errors))

class ReviewSerializerTests(TestCase):
    
    def setUp(self):
        self.reviewer = User.objects.create_user(username="rev1", email="rev1@example.com", password="pass", role="client")
        self.reviewee = User.objects.create_user(username="rev2", email="rev2@example.com", password="pass", role="worker")
        self.job = JobPosting.objects.create(title="Reviewed Job", description="...", posted_by=self.reviewer)

    def test_review_serializer_valid(self):
        data = {
            "reviewee_id": self.reviewee.id,
            "job_id": self.job.id,
            "rating": 5,
            "comment": "Good work"
        }
        
        factory = APIRequestFactory()
        request = factory.post('/')
        request.user = self.reviewer
        
        serializer = ReviewSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())

    def test_review_self_invalid(self):
        data = {
            "reviewee_id": self.reviewer.id,  # Reviewing self
            "job_id": self.job.id,
            "rating": 5,
            "comment": "Good work"
        }
        
        factory = APIRequestFactory()
        request = factory.post('/')
        request.user = self.reviewer
        
        serializer = ReviewSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn("Cannot review yourself", str(serializer.errors))

    def test_invalid_rating(self):
        data = {
            "reviewee_id": self.reviewee.id,
            "job_id": self.job.id,
            "rating": 6,  # Invalid rating
            "comment": "Good work"
        }
        
        factory = APIRequestFactory()
        request = factory.post('/')
        request.user = self.reviewer
        
        serializer = ReviewSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn("Rating must be between 1 and 5", str(serializer.errors))

class WorkerProfileSerializerTests(TestCase):
    
    def setUp(self):
        self.worker = User.objects.create_user(username="worker", email="worker@example.com", password="pass123", role="worker")
        self.skill = Skill.objects.create(name="Python")

    def test_worker_profile_create_with_skills(self):
        data = {
            "title": "Full Stack Developer",
            "bio": "Experienced developer",
            "hourly_rate": 50.00,
            "currency": "USD",
            "experience_years": 5,
            "skill_ids": [self.skill.id]
        }
        
        serializer = WorkerProfileSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        profile = serializer.save(user=self.worker)
        self.assertEqual(profile.title, "Full Stack Developer")
        self.assertIn(self.skill, profile.skills.all())

    def test_worker_profile_update_skills(self):
        profile = WorkerProfile.objects.create(
            user=self.worker,
            title="Developer",
            bio="Test bio"
        )
        
        new_skill = Skill.objects.create(name="JavaScript")
        data = {
            "title": "Senior Developer",
            "skill_ids": [new_skill.id]
        }
        
        serializer = WorkerProfileSerializer(instance=profile, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_profile = serializer.save()
        self.assertEqual(updated_profile.title, "Senior Developer")
        self.assertIn(new_skill, updated_profile.skills.all())
