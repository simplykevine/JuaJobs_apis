from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from api.models import User, JobPosting, Application, Review, WorkerProfile, Skill, Category
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework_simplejwt.tokens import RefreshToken

class UserAuthTests(APITestCase):
    
    def setUp(self):
        self.signup_url = reverse('signup')
        self.login_url = reverse('login')

    def test_user_signup(self):
        response = self.client.post(self.signup_url, {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123",
            "password_confirm": "testpass123",
            "role": "worker"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertIn("user", response.data)

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
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.get(reverse('test-token'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

class JobPostingTests(APITestCase):
    
    def setUp(self):
        self.client_user = User.objects.create_user(
            email="client@example.com", 
            username="client", 
            password="pass123", 
            role="client"
        )
        self.worker_user = User.objects.create_user(
            email="worker@example.com", 
            username="worker", 
            password="pass123", 
            role="worker"
        )
        self.category = Category.objects.create(name="Technology")
        self.skill = Skill.objects.create(name="Python")

    def authenticate_client(self):
        refresh = RefreshToken.for_user(self.client_user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def authenticate_worker(self):
        refresh = RefreshToken.for_user(self.worker_user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def test_create_job_posting_as_client(self):
        self.authenticate_client()
        response = self.client.post('/api/jobs/', {
            "title": "Test Job",
            "description": "Job Description",
            "category_id": self.category.id,
            "skill_ids": [self.skill.id]
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Test Job")

    def test_create_job_posting_as_worker_forbidden(self):
        self.authenticate_worker()
        response = self.client.post('/api/jobs/', {
            "title": "Test Job",
            "description": "Job Description"
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_jobs_public(self):
        JobPosting.objects.create(
            title="Public Job",
            description="Description",
            posted_by=self.client_user,
            status="active"
        )
        response = self.client.get('/api/jobs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_my_jobs_endpoint(self):
        self.authenticate_client()
        JobPosting.objects.create(
            title="My Job",
            description="Description",
            posted_by=self.client_user
        )
        response = self.client.get('/api/jobs/my_jobs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

class ApplicationTests(APITestCase):
    
    def setUp(self):
        self.worker = User.objects.create_user(
            email="worker@example.com", 
            username="worker", 
            password="pass123", 
            role="worker"
        )
        self.client_user = User.objects.create_user(
            email="client@example.com", 
            username="client", 
            password="pass123", 
            role="client"
        )
        self.job = JobPosting.objects.create(
            title="Dev Job", 
            description="details", 
            posted_by=self.client_user,
            status="active"
        )

    def authenticate_worker(self):
        refresh = RefreshToken.for_user(self.worker)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def authenticate_client(self):
        refresh = RefreshToken.for_user(self.client_user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def test_create_application(self):
        self.authenticate_worker()
        fake_file = SimpleUploadedFile("cover.pdf", b"fake content", content_type="application/pdf")
        response = self.client.post('/api/applications/', {
            "job_id": self.job.id,
            "cover_letter": fake_file
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_client_cannot_apply(self):
        self.authenticate_client()
        fake_file = SimpleUploadedFile("cover.pdf", b"fake content", content_type="application/pdf")
        response = self.client.post('/api/applications/', {
            "job_id": self.job.id,
            "cover_letter": fake_file
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_application_status(self):
        self.authenticate_worker()
        fake_file = SimpleUploadedFile("cover.pdf", b"fake content", content_type="application/pdf")
        application = Application.objects.create(
            job=self.job,
            worker=self.worker,
            cover_letter=fake_file
        )
        
        # Switch to client to update status
        self.authenticate_client()
        response = self.client.patch(f'/api/applications/{application.id}/update_status/', {
            "status": "accepted"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "accepted")

class ReviewTests(APITestCase):
    
    def setUp(self):
        self.reviewer = User.objects.create_user(
            email="rev1@example.com", 
            username="rev1", 
            password="pass123", 
            role="client"
        )
        self.reviewee = User.objects.create_user(
            email="rev2@example.com", 
            username="rev2", 
            password="pass123", 
            role="worker"
        )
        self.job = JobPosting.objects.create(
            title="Reviewed Job", 
            description="desc", 
            posted_by=self.reviewer
        )

    def authenticate_reviewer(self):
        refresh = RefreshToken.for_user(self.reviewer)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def test_create_review(self):
        self.authenticate_reviewer()
        response = self.client.post('/api/reviews/', {
            "reviewee_id": self.reviewee.id,
            "job_id": self.job.id,
            "rating": 5,
            "comment": "Excellent collaboration!"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_reviews_endpoint(self):
        Review.objects.create(
            reviewer=self.reviewer,
            reviewee=self.reviewee,
            job=self.job,
            rating=5,
            comment="Great work"
        )
        
        response = self.client.get(f'/api/reviews/user_reviews/?user_id={self.reviewee.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("average_rating", response.data)
        self.assertIn("total_reviews", response.data)

class WorkerProfileTests(APITestCase):
    
    def setUp(self):
        self.worker = User.objects.create_user(
            email="worker@example.com", 
            username="worker", 
            password="pass123", 
            role="worker"
        )
        self.skill = Skill.objects.create(name="Python")

    def authenticate_worker(self):
        refresh = RefreshToken.for_user(self.worker)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def test_create_worker_profile(self):
        self.authenticate_worker()
        response = self.client.post('/api/profiles/', {
            "title": "Full Stack Developer",
            "bio": "Experienced developer",
            "hourly_rate": 50.00,
            "currency": "USD",
            "experience_years": 5,
            "skill_ids": [self.skill.id]
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Full Stack Developer")

    def test_list_worker_profiles(self):
        WorkerProfile.objects.create(
            user=self.worker,
            title="Developer",
            bio="Test bio"
        )
        response = self.client.get('/api/profiles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

class DashboardTests(APITestCase):
    
    def setUp(self):
        self.client_user = User.objects.create_user(
            email="client@example.com", 
            username="client", 
            password="pass123", 
            role="client"
        )
        self.worker_user = User.objects.create_user(
            email="worker@example.com", 
            username="worker", 
            password="pass123", 
            role="worker"
        )

    def authenticate_client(self):
        refresh = RefreshToken.for_user(self.client_user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def authenticate_worker(self):
        refresh = RefreshToken.for_user(self.worker_user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def test_client_dashboard_stats(self):
        self.authenticate_client()
        JobPosting.objects.create(
            title="Test Job",
            description="Description",
            posted_by=self.client_user
        )
        
        response = self.client.get('/api/dashboard/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_jobs_posted", response.data)
        self.assertEqual(response.data["total_jobs_posted"], 1)

    def test_worker_dashboard_stats(self):
        self.authenticate_worker()
        response = self.client.get('/api/dashboard/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_applications", response.data)
        self.assertIn("profile_exists", response.data)

    def test_platform_stats_public(self):
        JobPosting.objects.create(
            title="Test Job",
            description="Description",
            posted_by=self.client_user
        )
        
        response = self.client.get('/api/platform/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_jobs", response.data)
        self.assertEqual(response.data["total_jobs"], 1)
