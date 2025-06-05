from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login


@csrf_exempt
def login_view(request):
    """Simple login view returning JSON response."""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"detail": "logged in"})
        return JsonResponse({"detail": "invalid credentials"}, status=400)
    return HttpResponse("login")

@login_required
def whoami(request):
    return JsonResponse({"username": request.user.username})
