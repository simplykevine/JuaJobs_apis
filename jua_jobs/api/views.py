from rest_framework import status, viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.db.models import Q, Avg, Count
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from drf_spectacular.utils import extend_schema, OpenApiExample

from .models import JobPosting, Application, Review, WorkerProfile, Skill, Category, PaymentTransaction, PaymentMethod
from .serializers import (
    JobPostingSerializer, ApplicationSerializer, ReviewSerializer,
    UserSignupSerializer, UserLoginSerializer, UserSerializer,
    WorkerProfileSerializer, SkillSerializer, CategorySerializer,
    PaymentTransactionSerializer, PaymentMethodSerializer
)
from .permissions import (
    IsOwnerOrReadOnly, IsClientRole, IsWorkerRole,
    IsApplicationOwnerOrJobOwner, IsReviewParticipant, IsProfileOwner
)
from .filters import (
    JobPostingFilter, ApplicationFilter, ReviewFilter,
    WorkerProfileFilter, UserFilter
)
from .utils.caching import CacheManager, cache_result

User = get_user_model()

class UserSignupView(APIView):
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        request=UserSignupSerializer,
        responses={201: UserSignupSerializer},
        examples=[
            OpenApiExample(
                'Worker Signup Example',
                summary='Sign up as a worker',
                description='Example of signing up as a worker with Kenyan phone number',
                value={
                    "email": "worker@example.com",
                    "username": "johnworker",
                    "password": "password123",
                    "password_confirm": "password123",
                    "role": "worker",
                    "country": "KE",
                    "phone_number": "+254712345678"
                },
                request_only=True,
            ),
            OpenApiExample(
                'Client Signup Example',
                summary='Sign up as a client',
                description='Example of signing up as a client',
                value={
                    "email": "client@example.com",
                    "username": "janeclient",
                    "password": "password123",
                    "password_confirm": "password123",
                    "role": "client",
                    "country": "NG",
                    "phone_number": "+234812345678"
                },
                request_only=True,
            ),
        ]
    )
    def post(self, request):
        """
        Create a new user account
        
        Register a new user as either a worker or client. Phone number format 
        must match the country code pattern.
        """
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({
                'message': 'User created successfully',
                'token': access_token,
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'role': user.role
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        request=UserLoginSerializer,
        responses={200: UserLoginSerializer},
        examples=[
            OpenApiExample(
                'Login Example',
                summary='User login',
                description='Login with email and password',
                value={
                    "email": "test@example.com",
                    "password": "password123"
                },
                request_only=True,
            ),
        ]
    )
    def post(self, request):
        """
        Login user and get JWT tokens
        
        Authenticate user with email and password, returns access and refresh tokens.
        """
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({
                'message': 'Logged in successfully',
                'token': access_token,
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'role': user.role
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    responses={200: dict},
    examples=[
        OpenApiExample(
            'Token Test Response',
            summary='Valid token response',
            description='Response when token is valid',
            value={
                "message": "Hello testuser, your token is valid!",
                "user_id": 1,
                "role": "worker"
            },
            response_only=True,
        ),
    ]
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def test_token(request):
    """
    Test if JWT token is valid
    
    Use this endpoint to verify that your JWT token is working correctly.
    """
    return Response({
        "message": f"Hello {request.user.username}, your token is valid!",
        "user_id": request.user.id,
        "role": request.user.role
    })

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = UserFilter
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['date_joined', 'username']
    ordering = ['-date_joined']

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_object(self):
        if self.kwargs.get('pk') == 'me':
            return self.request.user
        return super().get_object()

class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description', 'category']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @cache_result(timeout=3600, prefix="skills")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @cache_result(timeout=3600, prefix="categories")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class WorkerProfileViewSet(viewsets.ModelViewSet):
    queryset = WorkerProfile.objects.select_related('user').prefetch_related('skills')
    serializer_class = WorkerProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsProfileOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = WorkerProfileFilter
    search_fields = ['title', 'bio', 'user__username', 'user__email']
    ordering_fields = ['created_at', 'hourly_rate', 'experience_years']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated, IsProfileOwner]
        return [permission() for permission in permission_classes]

class JobPostingViewSet(viewsets.ModelViewSet):
    queryset = JobPosting.objects.select_related('posted_by', 'category').prefetch_related('required_skills')
    serializer_class = JobPostingSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = JobPostingFilter
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['created_at', 'salary_min', 'salary_max', 'deadline']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated, IsClientRole]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        job = serializer.save(posted_by=self.request.user)
        # Invalidate cache after creating new job
        CacheManager.invalidate_job_cache(job.id)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list':
            # Only show active jobs for general listing
            if not self.request.user.is_authenticated or self.request.user.role != 'client':
                queryset = queryset.filter(status='active')
        return queryset

    @action(detail=True, methods=['get'])
    def applications(self, request, pk=None):
        job = self.get_object()
        if job.posted_by != request.user:
            return Response(
                {'error': 'You can only view applications for your own jobs'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        applications = job.applications.select_related('worker')
        serializer = ApplicationSerializer(applications, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_jobs(self, request):
        if request.user.role != 'client':
            return Response(
                {'error': 'Only clients can view their jobs'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        jobs = self.get_queryset().filter(posted_by=request.user)
        page = self.paginate_queryset(jobs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(jobs, many=True)
        return Response(serializer.data)

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.select_related('worker', 'job', 'job__posted_by')
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ApplicationFilter
    ordering_fields = ['applied_at', 'updated_at']
    ordering = ['-applied_at']

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated, IsWorkerRole]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsApplicationOwnerOrJobOwner]
        else:
            permission_classes = [permissions.IsAuthenticated, IsApplicationOwnerOrJobOwner]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        job_id = serializer.validated_data['job_id']
        job = get_object_or_404(JobPosting, id=job_id)
        serializer.save(worker=self.request.user, job=job)

    def get_queryset(self):
        user = self.request.user
        if user.role == 'worker':
            # Workers see their own applications
            return self.queryset.filter(worker=user)
        elif user.role == 'client':
            # Clients see applications to their jobs
            return self.queryset.filter(job__posted_by=user)
        return self.queryset.none()

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        application = self.get_object()
        
        # Only job owner can update application status
        if application.job.posted_by != request.user:
            return Response(
                {'error': 'Only job owner can update application status'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_status = request.data.get('status')
        if new_status not in ['accepted', 'rejected']:
            return Response(
                {'error': 'Status must be either accepted or rejected'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        application.status = new_status
        application.save()
        
        serializer = self.get_serializer(application)
        return Response(serializer.data)

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('reviewer', 'reviewee', 'job')
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsReviewParticipant]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ReviewFilter
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        reviewee_id = serializer.validated_data['reviewee_id']
        job_id = serializer.validated_data['job_id']
        reviewee = get_object_or_404(User, id=reviewee_id)
        job = get_object_or_404(JobPosting, id=job_id)
        serializer.save(reviewer=self.request.user, reviewee=reviewee, job=job)

    @action(detail=False, methods=['get'])
    def user_reviews(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reviews = self.get_queryset().filter(reviewee_id=user_id)
        
        # Calculate average rating
        avg_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
        rating_counts = reviews.values('rating').annotate(count=Count('rating'))
        
        # Handle pagination properly
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # Create custom paginated response with additional data
            paginated_response = self.get_paginated_response(serializer.data)
            
            # Add the additional data to the paginated response
            paginated_response.data.update({
                'average_rating': round(avg_rating, 2) if avg_rating else None,
                'total_reviews': reviews.count(),
                'rating_distribution': list(rating_counts)
            })
            return paginated_response
        
        # Non-paginated response
        serializer = self.get_serializer(reviews, many=True)
        return Response({
            'reviews': serializer.data,
            'average_rating': round(avg_rating, 2) if avg_rating else None,
            'total_reviews': reviews.count(),
            'rating_distribution': list(rating_counts)
        })

    def get_permissions(self):
        # Allow unauthenticated access to user_reviews action
        if self.action == 'user_reviews':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated, IsReviewParticipant]
        return [permission() for permission in permission_classes]

class PaymentTransactionViewSet(viewsets.ModelViewSet):
    queryset = PaymentTransaction.objects.select_related('sender', 'receiver', 'job')
    serializer_class = PaymentTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        # Users can only see their own transactions
        return self.queryset.filter(Q(sender=user) | Q(receiver=user))

    def perform_create(self, serializer):
        import uuid
        reference_id = str(uuid.uuid4())
        receiver_id = serializer.validated_data['receiver_id']
        job_id = serializer.validated_data.get('job_id')
        
        receiver = get_object_or_404(User, id=receiver_id)
        job = None
        if job_id:
            job = get_object_or_404(JobPosting, id=job_id)
        
        serializer.save(
            sender=self.request.user,
            receiver=receiver,
            job=job,
            reference_id=reference_id
        )

class PaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = PaymentMethod.objects.select_related('user')
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        # Users can only see their own payment methods
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        payment_method = self.get_object()
        
        # Remove default from other payment methods
        PaymentMethod.objects.filter(user=request.user, is_default=True).update(is_default=False)
        
        # Set this as default
        payment_method.is_default = True
        payment_method.save()
        
        serializer = self.get_serializer(payment_method)
        return Response(serializer.data)

# Analytics and Dashboard Views
@extend_schema(
    responses={200: dict},
    examples=[
        OpenApiExample(
            'Dashboard Stats Response',
            summary='User dashboard statistics',
            description='Statistics for authenticated user based on their role',
            value={
                "total_applications": 5,
                "pending_applications": 2,
                "accepted_applications": 2,
                "profile_exists": True
            },
            response_only=True,
        ),
    ]
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    """
    Get dashboard statistics for the authenticated user
    
    Returns different statistics based on user role (client or worker).
    """
    user = request.user
    
    if user.role == 'client':
        stats = {
            'total_jobs_posted': JobPosting.objects.filter(posted_by=user).count(),
            'active_jobs': JobPosting.objects.filter(posted_by=user, status='active').count(),
            'total_applications': Application.objects.filter(job__posted_by=user).count(),
            'pending_applications': Application.objects.filter(
                job__posted_by=user, status='pending'
            ).count(),
        }
    elif user.role == 'worker':
        stats = {
            'total_applications': Application.objects.filter(worker=user).count(),
            'pending_applications': Application.objects.filter(
                worker=user, status='pending'
            ).count(),
            'accepted_applications': Application.objects.filter(
                worker=user, status='accepted'
            ).count(),
            'profile_exists': hasattr(user, 'worker_profile'),
        }
    else:
        stats = {}
    
    return Response(stats)

@extend_schema(
    responses={200: dict},
    examples=[
        OpenApiExample(
            'Platform Stats Response',
            summary='Platform statistics',
            description='Overall platform statistics available to everyone',
            value={
                "total_jobs": 150,
                "active_jobs": 45,
                "total_workers": 89,
                "total_clients": 23,
                "total_applications": 234,
                "total_reviews": 67
            },
            response_only=True,
        ),
    ]
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def platform_stats(request):
    """
    Get overall platform statistics
    
    Public endpoint that returns general platform statistics.
    """
    stats = {
        'total_jobs': JobPosting.objects.count(),
        'active_jobs': JobPosting.objects.filter(status='active').count(),
        'total_workers': User.objects.filter(role='worker').count(),
        'total_clients': User.objects.filter(role='client').count(),
        'total_applications': Application.objects.count(),
        'total_reviews': Review.objects.count(),
    }
    return Response(stats)
