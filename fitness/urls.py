from django.urls import path
from django.http import HttpResponse

def _index(request):
    return HttpResponse("OK - fitness index (temporary)")

urlpatterns = [
    path('', _index, name='index'),
]