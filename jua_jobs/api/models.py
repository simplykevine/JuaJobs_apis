from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

# Custom user manager
class UserManager(BaseUserManager):
    def create_user(self, email, username=None, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address.')
        
        email = self.normalize_email(email)
        if not username:
            username = email.split('@')[0]
            
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)

class User(AbstractUser):
    email = models.EmailField(unique=True)

    ROLE_CHOICES = (
        ('client', 'Client'),
        ('worker', 'Worker'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='worker')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.email

class JobPosting(models.Model):
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('freelance', 'Freelance'),
        ('internship', 'Internship'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('closed', 'Closed'),
        ('filled', 'Filled'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField(blank=True, help_text="Job requirements and qualifications")
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='full_time')
    location = models.CharField(max_length=255, blank=True)
    remote_work = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    posted_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='job_postings',
        null=True 
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateTimeField(null=True, blank=True, help_text="Application deadline")


class Application(models.Model):
    worker = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications')
    # cover_letter = models.TextField()
    cover_letter = models.FileField(upload_to='cover_letters/')
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')],
        default='pending'
    )
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('worker', 'job')
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.worker.email} applied to {self.job.title}"

class Review(models.Model):
    reviewer = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='given_reviews')
    reviewee = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='received_reviews')
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.reviewer.email} for {self.reviewee.email}"
