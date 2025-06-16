from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Skill, Category, JobPosting, WorkerProfile, 
    Application, Review, PaymentTransaction
)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'country')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'phone_number', 'country', 'city', 'email_verified', 'phone_verified')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('email', 'role', 'phone_number', 'country', 'city')
        }),
    )

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'created_at')
    list_filter = ('parent', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('title', 'posted_by', 'status', 'employment_type', 'created_at')
    list_filter = ('status', 'employment_type', 'remote_work', 'created_at')
    search_fields = ('title', 'description', 'location')
    ordering = ('-created_at',)
    filter_horizontal = ('required_skills',)

@admin.register(WorkerProfile)
class WorkerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'hourly_rate', 'currency', 'experience_years')
    list_filter = ('currency', 'availability', 'created_at')
    search_fields = ('user__email', 'title', 'bio')
    ordering = ('-created_at',)
    filter_horizontal = ('skills',)

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('worker', 'job', 'status', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('worker__email', 'job__title')
    ordering = ('-applied_at',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'reviewee', 'job', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('reviewer__email', 'reviewee__email', 'job__title')
    ordering = ('-created_at',)

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('reference_id', 'transaction_type', 'status', 'amount', 'currency', 'created_at')
    list_filter = ('transaction_type', 'status', 'currency', 'created_at')
    search_fields = ('reference_id', 'sender__email', 'receiver__email')
    ordering = ('-created_at',)
    readonly_fields = ('reference_id',)
