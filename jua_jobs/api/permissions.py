from rest_framework import permissions
from .models import JobPosting, Application

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.posted_by == request.user

class IsClientRole(permissions.BasePermission):
    """
    Custom permission to only allow clients to create job postings.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'client'

class IsWorkerRole(permissions.BasePermission):
    """
    Custom permission to only allow workers to apply for jobs.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'worker'

class IsApplicationOwnerOrJobOwner(permissions.BasePermission):
    """
    Custom permission for applications - worker can view their own applications,
    client can view applications to their jobs.
    """
    def has_object_permission(self, request, view, obj):
        # Worker can access their own applications
        if obj.worker == request.user:
            return True
        
        # Client can access applications to their jobs
        if obj.job.posted_by == request.user:
            return True
        
        return False

class IsReviewParticipant(permissions.BasePermission):
    """
    Custom permission for reviews - only job participants can create reviews.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.method == 'POST':
            job_id = request.data.get('job_id')
            if job_id:
                try:
                    job = JobPosting.objects.get(id=job_id)
                    # Check if user is job owner or has applied to the job
                    if job.posted_by == request.user:
                        return True
                    if Application.objects.filter(job=job, worker=request.user).exists():
                        return True
                except JobPosting.DoesNotExist:
                    pass
            return False
        
        return True

    def has_object_permission(self, request, view, obj):
        # Only reviewer can edit their own review
        return obj.reviewer == request.user

class IsProfileOwner(permissions.BasePermission):
    """
    Custom permission for worker profiles.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for profile owner
        return obj.user == request.user
