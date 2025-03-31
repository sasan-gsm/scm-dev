from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET

# Create your views here.


@require_GET
def health_check(request):
    """
    Simple health check endpoint for monitoring and Docker healthchecks.
    Returns a 200 OK response if the application is running.
    """
    return JsonResponse({"status": "ok"})
