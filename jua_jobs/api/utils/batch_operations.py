from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
import json

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def batch_operations(request):
    """
    Handle batch operations for multiple API calls in a single request
    """
    operations = request.data.get('operations', [])
    sequential = request.data.get('sequential', False)
    
    if not operations:
        return Response(
            {'error': 'No operations provided'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if len(operations) > 10:  # Limit batch size
        return Response(
            {'error': 'Maximum 10 operations allowed per batch'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    results = []
    
    if sequential:
        # Execute operations sequentially with transaction
        with transaction.atomic():
            for operation in operations:
                result = execute_operation(operation, request)
                results.append(result)
                
                # Stop on error if sequential
                if result['status'] >= 400:
                    break
    else:
        # Execute operations independently
        for operation in operations:
            result = execute_operation(operation, request)
            results.append(result)
    
    return Response({'results': results})

def execute_operation(operation, request):
    """Execute a single operation within a batch"""
    try:
        method = operation.get('method', 'GET').upper()
        path = operation.get('path', '')
        operation_id = operation.get('id', '')
        data = operation.get('data', {})
        
        # Simple operation execution (in real implementation, you'd route to actual views)
        if method == 'GET' and path.startswith('/jobs'):
            from api.models import JobPosting
            from api.serializers import JobPostingSerializer
            
            if path == '/jobs':
                jobs = JobPosting.objects.filter(status='active')[:5]
                serializer = JobPostingSerializer(jobs, many=True)
                return {
                    'id': operation_id,
                    'status': 200,
                    'body': serializer.data
                }
        
        # Add more operation handlers as needed
        
        return {
            'id': operation_id,
            'status': 501,
            'body': {'error': 'Operation not implemented'}
        }
        
    except Exception as e:
        return {
            'id': operation.get('id', ''),
            'status': 500,
            'body': {'error': str(e)}
        }

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_job_upload(request):
    """
    Handle bulk job posting upload
    """
    jobs_data = request.data.get('jobs', [])
    continue_on_error = request.data.get('continue_on_error', True)
    
    if not jobs_data:
        return Response(
            {'error': 'No jobs data provided'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if len(jobs_data) > 50:  # Limit bulk upload size
        return Response(
            {'error': 'Maximum 50 jobs allowed per bulk upload'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    from api.serializers import JobPostingSerializer
    
    created_jobs = []
    errors = []
    
    for i, job_data in enumerate(jobs_data):
        try:
            serializer = JobPostingSerializer(data=job_data, context={'request': request})
            if serializer.is_valid():
                job = serializer.save(posted_by=request.user)
                created_jobs.append({
                    'index': i,
                    'id': job.id,
                    'title': job.title,
                    'status': 'created'
                })
            else:
                errors.append({
                    'index': i,
                    'errors': serializer.errors
                })
                if not continue_on_error:
                    break
        except Exception as e:
            errors.append({
                'index': i,
                'error': str(e)
            })
            if not continue_on_error:
                break
    
    return Response({
        'created_jobs': created_jobs,
        'errors': errors,
        'summary': {
            'total_submitted': len(jobs_data),
            'successful': len(created_jobs),
            'failed': len(errors)
        }
    })
