from django.urls import path
from django.views.generic import TemplateView


urlpatterns = [
    path('', TemplateView.as_view(template_name="index.html")),
    path('create-new-list/', TemplateView.as_view(template_name="index.html")),
    path('all-lists/', TemplateView.as_view(template_name="index.html")),
    path('lists/<int:id>/', TemplateView.as_view(template_name="index.html")),
    path('profile/', TemplateView.as_view(template_name="index.html")),
    path('settings/', TemplateView.as_view(template_name="index.html")),
    path('*', TemplateView.as_view(template_name="index.html"))
]
 