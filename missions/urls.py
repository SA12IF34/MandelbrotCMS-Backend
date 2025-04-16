from django.urls import path
from django.views.generic import TemplateView


urlpatterns = [
    path('', TemplateView(template_name="index.html")),
    path('create-new-list/', TemplateView(template_name="index.html")),
    path('all-lists/', TemplateView(template_name="index.html")),
    path('lists/<int:id>/', TemplateView(template_name="index.html")),
    path('profile/', TemplateView(template_name="index.html")),
    path('settings/', TemplateView(template_name="index.html")),
    path('*', TemplateView(template_name="index.html"))
]
