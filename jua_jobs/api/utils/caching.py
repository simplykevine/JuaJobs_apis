from django.core.cache import cache
from django.conf import settings
from functools import wraps
import hashlib
import json

def cache_key_generator(prefix, *args, **kwargs):
    """Generate a cache key from function arguments"""
    key_data = {
        'args': args,
        'kwargs': kwargs
    }
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    key_hash = hashlib.md5(key_string.encode()).hexdigest()
    return f"{prefix}:{key_hash}"

def cache_result(timeout=300, prefix="api"):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = cache_key_generator(f"{prefix}:{func.__name__}", *args, **kwargs)
            result = cache.get(cache_key)
            
            if result is None:
                result = func(*args, **kwargs)
                cache.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator

def invalidate_cache_pattern(pattern):
    """Invalidate cache keys matching a pattern"""
    if hasattr(cache, 'delete_pattern'):
        cache.delete_pattern(pattern)
    else:
        # Fallback for simple cache backends
        cache.clear()

class CacheManager:
    """Centralized cache management for JuaJobs API"""
    
    @staticmethod
    def get_job_cache_key(job_id):
        return f"job:{job_id}"
    
    @staticmethod
    def get_user_cache_key(user_id):
        return f"user:{user_id}"
    
    @staticmethod
    def get_application_cache_key(application_id):
        return f"application:{application_id}"
    
    @staticmethod
    def get_jobs_list_cache_key(filters=None):
        if filters:
            filter_hash = hashlib.md5(json.dumps(filters, sort_keys=True).encode()).hexdigest()
            return f"jobs_list:{filter_hash}"
        return "jobs_list:all"
    
    @staticmethod
    def invalidate_job_cache(job_id):
        cache_key = CacheManager.get_job_cache_key(job_id)
        cache.delete(cache_key)
        # Also invalidate related caches
        invalidate_cache_pattern("jobs_list:*")
    
    @staticmethod
    def invalidate_user_cache(user_id):
        cache_key = CacheManager.get_user_cache_key(user_id)
        cache.delete(cache_key)
    
    @staticmethod
    def cache_job_data(job_id, data, timeout=3600):
        cache_key = CacheManager.get_job_cache_key(job_id)
        cache.set(cache_key, data, timeout)
    
    @staticmethod
    def get_cached_job_data(job_id):
        cache_key = CacheManager.get_job_cache_key(job_id)
        return cache.get(cache_key)

# Performance monitoring utilities
class PerformanceMonitor:
    """Simple performance monitoring for API endpoints"""
    
    @staticmethod
    def log_query_count(func):
        """Decorator to log database query count"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            from django.db import connection
            initial_queries = len(connection.queries)
            
            result = func(*args, **kwargs)
            
            final_queries = len(connection.queries)
            query_count = final_queries - initial_queries
            
            if query_count > 10:  # Log if more than 10 queries
                import logging
                logger = logging.getLogger('api')
                logger.warning(f"High query count in {func.__name__}: {query_count} queries")
            
            return result
        return wrapper
