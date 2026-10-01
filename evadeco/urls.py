from django.contrib import admin
from django.urls import include, path
from django.http import HttpResponse

def check_ok(request):
    return HttpResponse("OK", status=200)

urlpatterns = [
    path("polls/", include("polls.urls")),
    path("admin/", admin.site.urls),
    path("", check_ok),
]