from django.http import JsonResponse
from functools import wraps

ACCEPTED_TOKEN = 'omni_pretest_token'

def require_token(func):
    @wraps(func)
    def _wrapped_view(request, *args, **kwargs):
        token = request.data.get('access_token')
        if token != ACCEPTED_TOKEN:
            return JsonResponse({'error': 'Unauthorized access token'}, status=401)
        return func(request, *args, **kwargs)
    return _wrapped_view