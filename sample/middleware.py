import time
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

RATE_LIMIT = 5  #requests
WINDOW_SECONDS = 300  # time
CACHE_PREFIX = 'rlmw:'

class RateLimitMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ip = self.get_ip(request)
        cache_key = f"{CACHE_PREFIX}{ip}"
        now = int(time.time())
        timestamps = cache.get(cache_key, [])
        valid_after = now - WINDOW_SECONDS
        timestamps = [ts for ts in timestamps if ts > valid_after]
        if len(timestamps) >= RATE_LIMIT:
            response = JsonResponse({'detail': 'Too Many Requests'}, status=429)
            response['X-RateLimit-Remaining'] = 0
            return response
        timestamps.append(now)
        cache.set(cache_key, timestamps, timeout=WINDOW_SECONDS)
        request.rate_limit_remaining = RATE_LIMIT - len(timestamps)
        return None

    def process_response(self, request, response):
        remaining = getattr(request, 'rate_limit_remaining', None)
        if remaining is not None:
            response['X-RateLimit-Remaining'] = remaining                               
        return response

    def get_ip(self, request):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if xff:
            ip = xff.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip
