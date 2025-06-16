from django.urls import reverse, resolve
from rest_framework.test import APITestCase
from rest_framework import status
from api.views import (
    UserSignupView,
    UserLoginView,
    test_token,
    JobPostingViewSet,
    ApplicationViewSet,
    ReviewViewSet,
)
from api.models import User
from rest_framework_simplejwt.tokens import RefreshToken


class URLTests(APITestCase):
    def authenticate_client(self):
        """Utility to authenticate the test client with a JWT token."""
        user = User.objects.create_user(email="test@example.com", username="testuser", password="testpass123")
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def test_signup_url_resolves(self):
        url = reverse('signup')
        self.assertEqual(resolve(url).func.view_class, UserSignupView)

    def test_login_url_resolves(self):
        url = reverse('login')
        self.assertEqual(resolve(url).func.view_class, UserLoginView)

    def test_test_token_url_resolves(self):
        url = reverse('test-token')
        self.assertEqual(resolve(url).func, test_token)

    def test_jobs_endpoint_exists(self):
        response = self.client.get('/api/jobs/')
        self.assertIn(response.status_code, [200, 401, 403])

    def test_applications_endpoint_exists(self):
        response = self.client.get('/api/applications/')
        self.assertIn(response.status_code, [200, 401, 403])

    def test_reviews_endpoint_exists(self):
        response = self.client.get('/api/reviews/')
        self.assertIn(response.status_code, [200, 401, 403])
