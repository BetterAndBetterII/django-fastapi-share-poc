from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def whoami(request):
    return JsonResponse({"username": request.user.username})
