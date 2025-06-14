from rest_framework.test import APITestCase
from models import User, JobPosting

class JobPostingTests(APITestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(username='client1', password='testpass', role='client')
        self.job = JobPosting.objects.create(client=self.client_user, title='Cleaner', description='Clean home', location='Kigali', budget=50)

    def test_get_job_list(self):
        self.client.force_authenticate(user=self.client_user)
        response = self.client.get('/api/jobs/')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data['results']), 1)