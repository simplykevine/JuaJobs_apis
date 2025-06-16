from django.test import TestCase
from django.contrib.auth import get_user_model
from api.models import JobPosting, Application, Review
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
import tempfile

User = get_user_model()

class UserModelTests(TestCase):

    def test_create_user_with_email(self):
        user = User.objects.create_user(email='user@example.com', password='pass123')
        self.assertEqual(user.email, 'user@example.com')
        self.assertTrue(user.check_password('pass123'))
        self.assertFalse(user.is_staff)

    def test_create_superuser(self):
        admin = User.objects.create_superuser(email='admin@example.com', password='adminpass')
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_email_is_unique(self):
        User.objects.create_user(email='user@example.com', password='pass123')
        with self.assertRaises(Exception):
            User.objects.create_user(email='user@example.com', password='pass456')


class JobPostingModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='poster@example.com', password='pass123')

    def test_create_job_posting(self):
        job = JobPosting.objects.create(
            title='Software Engineer',
            description='Develop applications.',
            posted_by=self.user
        )
        self.assertEqual(job.title, 'Software Engineer')
        self.assertEqual(job.posted_by.email, 'poster@example.com')


class ApplicationModelTests(TestCase):

    def setUp(self):
        self.worker = User.objects.create_user(email='worker@example.com', password='pass123')
        self.poster = User.objects.create_user(email='poster@example.com', password='pass123')
        self.job = JobPosting.objects.create(
            title='Frontend Developer',
            description='Work with React.js',
            posted_by=self.poster
        )

    def test_create_application(self):
        fake_file = SimpleUploadedFile("cv.pdf", b"file_content", content_type="application/pdf")
        app = Application.objects.create(worker=self.worker, job=self.job, cover_letter=fake_file)
        self.assertEqual(app.status, 'pending')
        self.assertEqual(str(app), f"{self.worker.email} applied to {self.job.title}")

    def test_unique_application(self):
        fake_file = SimpleUploadedFile("cv.pdf", b"file_content", content_type="application/pdf")
        Application.objects.create(worker=self.worker, job=self.job, cover_letter=fake_file)
        with self.assertRaises(Exception):
            Application.objects.create(worker=self.worker, job=self.job, cover_letter=fake_file)


class ReviewModelTests(TestCase):

    def setUp(self):
        self.reviewer = User.objects.create_user(email='reviewer@example.com', password='pass123')
        self.reviewee = User.objects.create_user(email='reviewee@example.com', password='pass123')
        self.job = JobPosting.objects.create(title='Backend Dev', description='API work', posted_by=self.reviewer)

    def test_create_review(self):
        review = Review.objects.create(
            reviewer=self.reviewer,
            reviewee=self.reviewee,
            job=self.job,
            rating=4,
            comment='Great work!'
        )
        self.assertEqual(review.rating, 4)
        self.assertEqual(str(review), f"Review by {self.reviewer.email} for {self.reviewee.email}")
