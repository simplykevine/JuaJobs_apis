from rest_framework import serializers
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, JobPosting, Application, Review
from django.contrib.auth import authenticate


class JobPostingSerializer(serializers.ModelSerializer):
    applicants = serializers.SerializerMethodField()

    class Meta:
        model = JobPosting
        fields = '__all__'  # Or list specific fields if preferred
        depth = 1  # Optional: Expand related fields

    def get_applicants(self, obj):
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

class ApplicationSerializer(serializers.ModelSerializer):
    cover_letter = serializers.FileField()

    class Meta:
        model = Application
        fields = ['id', 'job', 'cover_letter', 'status', 'applied_at']
        read_only_fields = ['status', 'applied_at']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'


from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
from django.contrib.auth import authenticate
from rest_framework import serializers

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password")
        
        data["user"] = user
        return data
