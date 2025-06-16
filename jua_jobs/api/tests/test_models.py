from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from api.models import JobPosting, Application, Review, WorkerProfile, Skill, Category, PaymentTransaction
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
        self.assertEqual(user.role, 'worker')  # default role

    def test_create_superuser(self):
        admin = User.objects.create_superuser(email='admin@example.com', password='adminpass')
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_email_is_unique(self):
        User.objects.create_user(email='user@example.com', password='pass123')
        with self.assertRaises(Exception):
            User.objects.create_user(email='user@example.com', password='pass456')

    def test_user_str_method(self):
        user = User.objects.create_user(email='test@example.com', password='pass123')
        self.assertEqual(str(user), 'test@example.com')

class SkillModelTests(TestCase):

    def test_create_skill(self):
        skill = Skill.objects.create(name='Python', description='Programming language')
        self.assertEqual(skill.name, 'Python')
        self.assertEqual(str(skill), 'Python')

    def test_skill_name_unique(self):
        Skill.objects.create(name='Python')
        with self.assertRaises(Exception):
            Skill.objects.create(name='Python')

class CategoryModelTests(TestCase):

    def test_create_category(self):
        category = Category.objects.create(name='Technology', description='Tech jobs')
        self.assertEqual(category.name, 'Technology')
        self.assertEqual(str(category), 'Technology')

    def test_category_hierarchy(self):
        parent = Category.objects.create(name='Technology')
        child = Category.objects.create(name='Web Development', parent=parent)
        self.assertEqual(child.parent, parent)

class JobPostingModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='poster@example.com', password='pass123', role='client')
        self.category = Category.objects.create(name='Technology')

    def test_create_job_posting(self):
        job = JobPosting.objects.create(
            title='Software Engineer',
            description='Develop applications.',
            posted_by=self.user,
            category=self.category
        )
        self.assertEqual(job.title, 'Software Engineer')
        self.assertEqual(job.posted_by.email, 'poster@example.com')
        self.assertEqual(job.status, 'active')  # default status

    def test_job_str_method(self):
        job = JobPosting.objects.create(
            title='Frontend Developer',
            description='Work with React.js',
            posted_by=self.user
        )
        self.assertEqual(str(job), 'Frontend Developer')

class WorkerProfileModelTests(TestCase):

    def setUp(self):
        self.worker = User.objects.create_user(email='worker@example.com', password='pass123', role='worker')
        self.skill = Skill.objects.create(name='Python')

    def test_create_worker_profile(self):
        profile = WorkerProfile.objects.create(
            user=self.worker,
            title='Full Stack Developer',
            bio='Experienced developer',
            hourly_rate=50.00
        )
        self.assertEqual(profile.title, 'Full Stack Developer')
        self.assertEqual(profile.user, self.worker)

    def test_worker_profile_str_method(self):
        profile = WorkerProfile.objects.create(
            user=self.worker,
            title='Backend Developer',
            bio='Python specialist'
        )
        self.assertEqual(str(profile), 'worker@example.com - Backend Developer')

class ApplicationModelTests(TestCase):

    def setUp(self):
        self.worker = User.objects.create_user(email='worker@example.com', password='pass123', role='worker')
        self.poster = User.objects.create_user(email='poster@example.com', password='pass123', role='client')
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
        fake_file1 = SimpleUploadedFile("cv1.pdf", b"file_content", content_type="application/pdf")
        fake_file2 = SimpleUploadedFile("cv2.pdf", b"file_content", content_type="application/pdf")
        Application.objects.create(worker=self.worker, job=self.job, cover_letter=fake_file1)
        with self.assertRaises(Exception):
            Application.objects.create(worker=self.worker, job=self.job, cover_letter=fake_file2)

class ReviewModelTests(TestCase):

    def setUp(self):
        self.reviewer = User.objects.create_user(email='reviewer@example.com', password='pass123', role='client')
        self.reviewee = User.objects.create_user(email='reviewee@example.com', password='pass123', role='worker')
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

    def test_review_rating_validation(self):
        # This would be handled by model validators in a real scenario
        review = Review(
            reviewer=self.reviewer,
            reviewee=self.reviewee,
            job=self.job,
            rating=6,  # Invalid rating
            comment='Test'
        )
        with self.assertRaises(ValidationError):
            review.full_clean()

class PaymentTransactionModelTests(TestCase):

    def setUp(self):
        self.sender = User.objects.create_user(email='sender@example.com', password='pass123', role='client')
        self.receiver = User.objects.create_user(email='receiver@example.com', password='pass123', role='worker')
        self.job = JobPosting.objects.create(
            title='Test Job',
            description='Test description',
            posted_by=self.sender
        )

    def test_create_payment_transaction(self):
        payment = PaymentTransaction.objects.create(
            transaction_type='job_payment',
            amount=1000.00,
            currency='USD',
            sender=self.sender,
            receiver=self.receiver,
            job=self.job,
            reference_id='PAY123456'
        )
        self.assertEqual(payment.amount, 1000.00)
        self.assertEqual(payment.status, 'pending')  # default status
        self.assertEqual(str(payment), 'job_payment - 1000.00 USD')
