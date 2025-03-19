from django.contrib import admin
from django.urls import path, re_path, include
from django.conf.urls.static import static
from django.views.static import serve

from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('authentication/', include('authentication.urls')),

    path('sessions_manager/', include('sessions_manager.urls')),
    path('learning_tracker/', include('learning_tracker.urls')),
    path('entertainment/', include('entertainment.urls')),
    path('missions/', include('missions.urls')),
    path('goals/', include('goals.urls')),

    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
