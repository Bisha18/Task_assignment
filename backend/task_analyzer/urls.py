from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>Smart Task Analyzer API is Running!</h1><p>Open <b>frontend/index.html</b> to use the app.</p>")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/tasks/', include('tasks.urls')),
    path('', home)
]