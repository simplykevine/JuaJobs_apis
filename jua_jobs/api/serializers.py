from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from .models import JobPosting, Application, Review, WorkerProfile, Skill, Category, PaymentTransaction

User = get_user_model()

class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password_confirm', 'role', 'phone_number', 'country', 'city']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid email or password")
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled")
            data["user"] = user
        else:
            raise serializers.ValidationError("Must include email and password")
        
        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone_number', 'country', 'city', 'date_joined']
        read_only_fields = ['id', 'date_joined']

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'description', 'category']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent']

class WorkerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    skill_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = WorkerProfile
        fields = ['id', 'user', 'title', 'bio', 'skills', 'skill_ids', 'hourly_rate', 
                 'currency', 'experience_years', 'availability', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        skill_ids = validated_data.pop('skill_ids', [])
        profile = WorkerProfile.objects.create(**validated_data)
        if skill_ids:
            profile.skills.set(skill_ids)
        return profile

    def update(self, instance, validated_data):
        skill_ids = validated_data.pop('skill_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if skill_ids is not None:
            instance.skills.set(skill_ids)
        return instance

class JobPostingSerializer(serializers.ModelSerializer):
    posted_by = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    required_skills = SkillSerializer(many=True, read_only=True)
    applicants = serializers.SerializerMethodField()
    application_count = serializers.SerializerMethodField()
    
    # Write-only fields for creation/update
    category_id = serializers.IntegerField(write_only=True, required=False)
    skill_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = JobPosting
        fields = ['id', 'title', 'description', 'requirements', 'salary_min', 'salary_max',
                 'employment_type', 'location', 'remote_work', 'status', 'posted_by',
                 'category', 'category_id', 'required_skills', 'skill_ids', 'deadline',
                 'created_at', 'updated_at', 'applicants', 'application_count']
        read_only_fields = ['id', 'posted_by', 'created_at', 'updated_at']

    def get_applicants(self, obj):
        if self.context.get('request') and self.context['request'].user == obj.posted_by:
            applications = obj.applications.select_related('worker')
            return [
                {
                    "worker_id": app.worker.id,
                    "worker_name": app.worker.username,
                    "worker_email": app.worker.email,
                    "cover_letter": app.cover_letter.url if app.cover_letter else None,
                    "status": app.status,
                    "applied_at": app.applied_at
                }
                for app in applications
            ]
        return []

    def get_application_count(self, obj):
        return obj.applications.count()

    def create(self, validated_data):
        category_id = validated_data.pop('category_id', None)
        skill_ids = validated_data.pop('skill_ids', [])
        
        job = JobPosting.objects.create(**validated_data)
        
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                job.category = category
                job.save()
            except Category.DoesNotExist:
                pass
        
        if skill_ids:
            job.required_skills.set(skill_ids)
        
        return job

    def update(self, instance, validated_data):
        category_id = validated_data.pop('category_id', None)
        skill_ids = validated_data.pop('skill_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if category_id is not None:
            try:
                category = Category.objects.get(id=category_id)
                instance.category = category
                instance.save()
            except Category.DoesNotExist:
                pass
        
        if skill_ids is not None:
            instance.required_skills.set(skill_ids)
        
        return instance

class ApplicationSerializer(serializers.ModelSerializer):
    worker = UserSerializer(read_only=True)
    job = JobPostingSerializer(read_only=True)
    job_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Application
        fields = ['id', 'worker', 'job', 'job_id', 'cover_letter', 'status', 'applied_at', 'updated_at']
        read_only_fields = ['id', 'worker', 'applied_at', 'updated_at']

    def validate_job_id(self, value):
        try:
            job = JobPosting.objects.get(id=value)
            if job.status not in ['active']:
                raise serializers.ValidationError("Cannot apply to inactive job")
            return value
        except JobPosting.DoesNotExist:
            raise serializers.ValidationError("Job does not exist")

    def validate(self, attrs):
        request = self.context.get('request')
        if request and request.user:
            job_id = attrs.get('job_id')
            if job_id:
                try:
                    job = JobPosting.objects.get(id=job_id)
                    if job.posted_by == request.user:
                        raise serializers.ValidationError("Cannot apply to your own job")
                    
                    # Check if already applied
                    if Application.objects.filter(worker=request.user, job=job).exists():
                        raise serializers.ValidationError("Already applied to this job")
                except JobPosting.DoesNotExist:
                    pass
        return attrs

class ReviewSerializer(serializers.ModelSerializer):
    reviewer = UserSerializer(read_only=True)
    reviewee = UserSerializer(read_only=True)
    job = JobPostingSerializer(read_only=True)
    
    # Write-only fields
    reviewee_id = serializers.IntegerField(write_only=True)
    job_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Review
        fields = ['id', 'reviewer', 'reviewee', 'reviewee_id', 'job', 'job_id', 
                 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'reviewer', 'created_at']

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value

    def validate(self, attrs):
        request = self.context.get('request')
        if request and request.user:
            reviewee_id = attrs.get('reviewee_id')
            job_id = attrs.get('job_id')
            
            if reviewee_id == request.user.id:
                raise serializers.ValidationError("Cannot review yourself")
            
            # Check if review already exists
            if Review.objects.filter(
                reviewer=request.user,
                reviewee_id=reviewee_id,
                job_id=job_id
            ).exists():
                raise serializers.ValidationError("Review already exists for this job")
        
        return attrs

class PaymentTransactionSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    job = JobPostingSerializer(read_only=True)
    
    # Write-only fields
    receiver_id = serializers.IntegerField(write_only=True)
    job_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = PaymentTransaction
        fields = ['id', 'transaction_type', 'status', 'amount', 'currency', 
                 'sender', 'receiver', 'receiver_id', 'job', 'job_id', 
                 'reference_id', 'payment_method', 'created_at', 'updated_at']
        read_only_fields = ['id', 'sender', 'reference_id', 'created_at', 'updated_at']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value
