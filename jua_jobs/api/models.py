from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
import re

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
    phone_number = models.CharField(max_length=15, blank=True)
    
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('worker', 'Worker'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='worker')
    
    # Location fields
    country = models.CharField(max_length=2, blank=True, help_text="ISO country code")
    city = models.CharField(max_length=100, blank=True)
    
    # Verification fields
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.email

    def clean(self):
        super().clean()
        # Validate phone number for African countries
        if self.phone_number and self.country:
            country_config = settings.AFRICAN_COUNTRIES.get(self.country)
            if country_config:
                pattern = country_config['phone_pattern']
                if not re.match(pattern, self.phone_number):
                    from django.core.exceptions import ValidationError
                    raise ValidationError(f'Invalid phone number format for {country_config["name"]}')

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

class JobPosting(models.Model):
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('freelance', 'Freelance'),
        ('internship', 'Internship'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
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
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    required_skills = models.ManyToManyField(Skill, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateTimeField(null=True, blank=True, help_text="Application deadline")

    class Meta:
        ordering = ['-created_at']  # Fix the UnorderedObjectListWarning

    def __str__(self):
        return self.title

class WorkerProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='worker_profile')
    title = models.CharField(max_length=200)
    bio = models.TextField()
    skills = models.ManyToManyField(Skill, blank=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    experience_years = models.PositiveIntegerField(default=0)
    availability = models.CharField(max_length=50, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.title}"

class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn')
    ]
    
    worker = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.FileField(upload_to='cover_letters/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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

    class Meta:
        unique_together = ('reviewer', 'reviewee', 'job')
        ordering = ['-created_at']  # Fix the UnorderedObjectListWarning

    def __str__(self):
        return f"Review by {self.reviewer.email} for {self.reviewee.email}"

class PaymentTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('job_payment', 'Job Payment'),
        ('platform_fee', 'Platform Fee'),
        ('withdrawal', 'Withdrawal'),
        ('refund', 'Refund'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    sender = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='sent_payments')
    receiver = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='received_payments')
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, null=True, blank=True)
    reference_id = models.CharField(max_length=100, unique=True)
    payment_method = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        # Format amount to always show 2 decimal places
        return f"{self.transaction_type} - {self.amount:.2f} {self.currency}"

# African Market Specific Models
class PaymentMethod(models.Model):
    PAYMENT_TYPES = [
        ('mpesa', 'M-Pesa'),
        ('airtel_money', 'Airtel Money'),
        ('mtn_mobile_money', 'MTN Mobile Money'),
        ('bank_transfer', 'Bank Transfer'),
        ('card', 'Credit/Debit Card'),
    ]
    
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='payment_methods')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    phone_number = models.CharField(max_length=15, blank=True)
    account_details = models.JSONField(default=dict)
    is_verified = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.get_payment_type_display()}"

    def clean(self):
        super().clean()
        # Validate mobile money phone numbers
        if self.payment_type in ['mpesa', 'airtel_money', 'mtn_mobile_money']:
            if not self.phone_number:
                from django.core.exceptions import ValidationError
                raise ValidationError('Phone number is required for mobile money payments')
            
            # Validate phone number format based on payment type and user country
            if self.user.country:
                country_config = settings.AFRICAN_COUNTRIES.get(self.user.country)
                if country_config:
                    pattern = country_config['phone_pattern']
                    if not re.match(pattern, self.phone_number):
                        from django.core.exceptions import ValidationError
                        raise ValidationError(f'Invalid phone number format for {country_config["name"]}')
