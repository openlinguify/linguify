from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})