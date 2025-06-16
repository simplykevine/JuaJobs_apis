import django_filters
from django.db.models import Q
from .models import JobPosting, Application, Review, WorkerProfile, User

class JobPostingFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    location = django_filters.CharFilter(lookup_expr='icontains')
    employment_type = django_filters.ChoiceFilter(choices=JobPosting.EMPLOYMENT_TYPE_CHOICES)
    status = django_filters.ChoiceFilter(choices=JobPosting.STATUS_CHOICES)
    remote_work = django_filters.BooleanFilter()
    salary_min = django_filters.NumberFilter(field_name='salary_min', lookup_expr='gte')
    salary_max = django_filters.NumberFilter(field_name='salary_max', lookup_expr='lte')
    category = django_filters.NumberFilter(field_name='category__id')
    skills = django_filters.CharFilter(method='filter_by_skills')
    posted_by = django_filters.NumberFilter(field_name='posted_by__id')
    
    class Meta:
        model = JobPosting
        fields = ['title', 'location', 'employment_type', 'status', 'remote_work', 
                 'salary_min', 'salary_max', 'category', 'skills', 'posted_by']
    
    def filter_by_skills(self, queryset, name, value):
        skill_names = [skill.strip() for skill in value.split(',')]
        return queryset.filter(required_skills__name__in=skill_names).distinct()

class ApplicationFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=Application.STATUS_CHOICES)
    job = django_filters.NumberFilter(field_name='job__id')
    worker = django_filters.NumberFilter(field_name='worker__id')
    applied_after = django_filters.DateTimeFilter(field_name='applied_at', lookup_expr='gte')
    applied_before = django_filters.DateTimeFilter(field_name='applied_at', lookup_expr='lte')
    
    class Meta:
        model = Application
        fields = ['status', 'job', 'worker', 'applied_after', 'applied_before']

class ReviewFilter(django_filters.FilterSet):
    rating = django_filters.NumberFilter()
    rating_gte = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    rating_lte = django_filters.NumberFilter(field_name='rating', lookup_expr='lte')
    reviewer = django_filters.NumberFilter(field_name='reviewer__id')
    reviewee = django_filters.NumberFilter(field_name='reviewee__id')
    job = django_filters.NumberFilter(field_name='job__id')
    
    class Meta:
        model = Review
        fields = ['rating', 'rating_gte', 'rating_lte', 'reviewer', 'reviewee', 'job']

class WorkerProfileFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    skills = django_filters.CharFilter(method='filter_by_skills')
    hourly_rate_min = django_filters.NumberFilter(field_name='hourly_rate', lookup_expr='gte')
    hourly_rate_max = django_filters.NumberFilter(field_name='hourly_rate', lookup_expr='lte')
    experience_years_min = django_filters.NumberFilter(field_name='experience_years', lookup_expr='gte')
    availability = django_filters.CharFilter(lookup_expr='icontains')
    country = django_filters.CharFilter(field_name='user__country')
    city = django_filters.CharFilter(field_name='user__city', lookup_expr='icontains')
    
    class Meta:
        model = WorkerProfile
        fields = ['title', 'skills', 'hourly_rate_min', 'hourly_rate_max', 
                 'experience_years_min', 'availability', 'country', 'city']
    
    def filter_by_skills(self, queryset, name, value):
        skill_names = [skill.strip() for skill in value.split(',')]
        return queryset.filter(skills__name__in=skill_names).distinct()

class UserFilter(django_filters.FilterSet):
    role = django_filters.ChoiceFilter(choices=User.ROLE_CHOICES)
    country = django_filters.CharFilter()
    city = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    username = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = User
        fields = ['role', 'country', 'city', 'email', 'username']
