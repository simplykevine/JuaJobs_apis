from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    JobPostingViewSet, ApplicationViewSet, ReviewViewSet,
    UserSignupView, UserLoginView, test_token, UserViewSet,
    WorkerProfileViewSet, SkillViewSet, CategoryViewSet,
    PaymentTransactionViewSet, dashboard_stats, platform_stats
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'skills', SkillViewSet, basename='skill')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'profiles', WorkerProfileViewSet, basename='workerprofile')
router.register(r'jobs', JobPostingViewSet, basename='jobposting')
router.register(r'applications', ApplicationViewSet, basename='application')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'payments', PaymentTransactionViewSet, basename='paymenttransaction')

urlpatterns = [
    path('', include(router.urls)),
    
    # Authentication endpoints
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('test-token/', test_token, name='test-token'),
    
    # Dashboard and analytics
    path('dashboard/stats/', dashboard_stats, name='dashboard-stats'),
    path('platform/stats/', platform_stats, name='platform-stats'),
]
