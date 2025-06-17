#!/usr/bin/env python
"""
Load sample data for JuaJobs API testing
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jua_jobs.settings')
django.setup()

from django.contrib.auth import get_user_model
from api.models import Skill, Category, JobPosting, WorkerProfile, PaymentMethod

User = get_user_model()

def create_sample_data():
    print("Creating sample data...")
    
    # Create skills
    skills_data = [
        {'name': 'Python', 'category': 'Programming', 'description': 'Python programming language'},
        {'name': 'JavaScript', 'category': 'Programming', 'description': 'JavaScript programming language'},
        {'name': 'Django', 'category': 'Framework', 'description': 'Django web framework'},
        {'name': 'React', 'category': 'Framework', 'description': 'React frontend framework'},
        {'name': 'Data Analysis', 'category': 'Analytics', 'description': 'Data analysis and visualization'},
        {'name': 'Mobile Development', 'category': 'Development', 'description': 'Mobile app development'},
        {'name': 'UI/UX Design', 'category': 'Design', 'description': 'User interface and experience design'},
        {'name': 'Digital Marketing', 'category': 'Marketing', 'description': 'Digital marketing and social media'},
    ]
    
    skills = []
    for skill_data in skills_data:
        skill, created = Skill.objects.get_or_create(
            name=skill_data['name'],
            defaults=skill_data
        )
        skills.append(skill)
        if created:
            print(f"Created skill: {skill.name}")
    
    # Create categories
    categories_data = [
        {'name': 'Technology', 'description': 'Technology and software development jobs'},
        {'name': 'Design', 'description': 'Design and creative jobs'},
        {'name': 'Marketing', 'description': 'Marketing and advertising jobs'},
        {'name': 'Writing', 'description': 'Content writing and copywriting jobs'},
        {'name': 'Business', 'description': 'Business and consulting jobs'},
    ]
    
    categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        categories.append(category)
        if created:
            print(f"Created category: {category.name}")
    
    # Create sample users
    users_data = [
        {
            'email': 'client1@example.com',
            'username': 'client1',
            'password': 'password123',
            'role': 'client',
            'first_name': 'John',
            'last_name': 'Doe',
            'country': 'KE',
            'city': 'Nairobi',
            'phone_number': '+254712345678'
        },
        {
            'email': 'worker1@example.com',
            'username': 'worker1',
            'password': 'password123',
            'role': 'worker',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'country': 'KE',
            'city': 'Nairobi',
            'phone_number': '+254712345679'
        },
        {
            'email': 'worker2@example.com',
            'username': 'worker2',
            'password': 'password123',
            'role': 'worker',
            'first_name': 'Mike',
            'last_name': 'Johnson',
            'country': 'NG',
            'city': 'Lagos',
            'phone_number': '+234812345678'
        }
    ]
    
    users = []
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults=user_data
        )
        if created:
            user.set_password(user_data['password'])
            user.save()
            print(f"Created user: {user.email}")
        users.append(user)
    
    # Create worker profiles
    worker_profiles_data = [
        {
            'user': users[1],  # worker1
            'title': 'Full Stack Developer',
            'bio': 'Experienced full stack developer with 5+ years of experience in Python and JavaScript.',
            'hourly_rate': 25.00,
            'currency': 'USD',
            'experience_years': 5,
            'availability': 'available'
        },
        {
            'user': users[2],  # worker2
            'title': 'UI/UX Designer',
            'bio': 'Creative designer specializing in user interface and user experience design.',
            'hourly_rate': 20.00,
            'currency': 'USD',
            'experience_years': 3,
            'availability': 'available'
        }
    ]
    
    for profile_data in worker_profiles_data:
        profile, created = WorkerProfile.objects.get_or_create(
            user=profile_data['user'],
            defaults=profile_data
        )
        if created:
            # Add skills to profile
            if profile.user.email == 'worker1@example.com':
                profile.skills.set([skills[0], skills[1], skills[2]])  # Python, JavaScript, Django
            else:
                profile.skills.set([skills[6]])  # UI/UX Design
            print(f"Created worker profile: {profile.title}")
    
    # Create sample jobs
    jobs_data = [
        {
            'title': 'Senior Python Developer',
            'description': 'We are looking for an experienced Python developer to join our team and work on exciting projects.',
            'requirements': 'Minimum 3 years of Python experience, Django knowledge preferred',
            'salary_min': 1500.00,
            'salary_max': 2500.00,
            'employment_type': 'full_time',
            'location': 'Nairobi, Kenya',
            'remote_work': True,
            'status': 'active',
            'posted_by': users[0],  # client1
            'category': categories[0]  # Technology
        },
        {
            'title': 'Mobile App Designer',
            'description': 'Looking for a creative designer to design mobile app interfaces.',
            'requirements': 'Experience with mobile design, Figma proficiency',
            'salary_min': 800.00,
            'salary_max': 1200.00,
            'employment_type': 'contract',
            'location': 'Remote',
            'remote_work': True,
            'status': 'active',
            'posted_by': users[0],  # client1
            'category': categories[1]  # Design
        }
    ]
    
    for job_data in jobs_data:
        job, created = JobPosting.objects.get_or_create(
            title=job_data['title'],
            posted_by=job_data['posted_by'],
            defaults=job_data
        )
        if created:
            # Add required skills
            if 'Python' in job.title:
                job.required_skills.set([skills[0], skills[2]])  # Python, Django
            else:
                job.required_skills.set([skills[6]])  # UI/UX Design
            print(f"Created job: {job.title}")
    
    # Create sample payment methods
    payment_methods_data = [
        {
            'user': users[1],  # worker1
            'payment_type': 'mpesa',
            'phone_number': '+254712345679',
            'is_default': True
        },
        {
            'user': users[2],  # worker2
            'payment_type': 'bank_transfer',
            'account_details': {'bank_name': 'First Bank', 'account_number': '1234567890'},
            'is_default': True
        }
    ]
    
    for pm_data in payment_methods_data:
        pm, created = PaymentMethod.objects.get_or_create(
            user=pm_data['user'],
            payment_type=pm_data['payment_type'],
            defaults=pm_data
        )
        if created:
            print(f"Created payment method: {pm.payment_type} for {pm.user.email}")
    
    print("Sample data creation completed!")

if __name__ == '__main__':
    create_sample_data()
