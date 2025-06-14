from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    JobPostingViewSet,
    ApplicationViewSet,
    ReviewViewSet,
    UserSignupView,
    UserLoginView,
    test_token,
)

# DRF Router setup
router = DefaultRouter()
router.register(r'jobs', JobPostingViewSet, basename='jobposting')
router.register(r'applications', ApplicationViewSet, basename='application')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),

    # Auth endpoints
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('test-token/', test_token, name='test-token'),
]
