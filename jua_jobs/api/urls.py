from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    JobPostingViewSet, ApplicationViewSet, ReviewViewSet,
    UserSignupView, UserLoginView, test_token, UserViewSet,
    WorkerProfileViewSet, SkillViewSet, CategoryViewSet,
    PaymentTransactionViewSet, PaymentMethodViewSet, dashboard_stats, platform_stats
)
from .utils.batch_operations import batch_operations, bulk_job_upload

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'skills', SkillViewSet, basename='skill')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'profiles', WorkerProfileViewSet, basename='workerprofile')
router.register(r'jobs', JobPostingViewSet, basename='jobposting')
router.register(r'applications', ApplicationViewSet, basename='application')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'payments', PaymentTransactionViewSet, basename='paymenttransaction')
router.register(r'payment-methods', PaymentMethodViewSet, basename='paymentmethod')

urlpatterns = [
    # Include router URLs - This creates the API root that you see
    path('', include(router.urls)),
    
    # Authentication endpoints
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('test-token/', test_token, name='test-token'),
    
    # Batch operations
    path('batch/', batch_operations, name='batch-operations'),
    path('jobs/bulk/', bulk_job_upload, name='bulk-job-upload'),
    
    # Dashboard and analytics
    path('dashboard/stats/', dashboard_stats, name='dashboard-stats'),
    path('platform/stats/', platform_stats, name='platform-stats'),
]
