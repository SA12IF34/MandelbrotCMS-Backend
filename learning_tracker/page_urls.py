from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name="index.html")),
    path('.*/', TemplateView.as_view(template_name="index.html"))
]

REACT_ROUTES = [
    'add-new/',
    'courses/<int:id>/',
    'not-found/'
]

for route in REACT_ROUTES:
    urlpatterns.append(path(route, TemplateView.as_view(template_name="index.html")))