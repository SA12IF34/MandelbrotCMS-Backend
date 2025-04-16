from django.shortcuts import render, redirect
from django.contrib import admin
from django.urls import path, re_path, include
from django.conf.urls.static import static
from django.views.static import serve
from django.views.generic import TemplateView

from django.conf import settings


def home_view(request):

    if not request.user.is_authenticated:
        return render(request, 'index.html')

    return redirect('/central')


urlpatterns = [
    path('', home_view),
    path('login/', TemplateView.as_view(template_name="index.html")),
    path('register/', TemplateView.as_view(template_name="index.html")),
    path('admin/', admin.site.urls),
    path('authentication/', include('authentication.urls')),

    path('central/', include('missions.urls')),
    path('sessions-manager/', include('sessions_manager.page_urls')),
    path('learning-tracker/', include('learning_tracker.page_urls')),

    path('sessions_manager/', include('sessions_manager.urls')),
    path('learning_tracker/', include('learning_tracker.urls')),
    path('entertainment/', include('entertainment.urls')),
    path('missions/', include('missions.api_urls')),
    path('goals/', include('goals.urls')),

    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
