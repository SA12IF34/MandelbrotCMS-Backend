from django.urls import path
from django.views.generic import TemplateView
from .views import NotesAPIs, NoteAPIs

urlpatterns = [
    path('apis/notes/', NotesAPIs.as_view(), name='notes'),
    path('apis/note/<int:pk>/', NoteAPIs.as_view(), name='note'),

    path('', TemplateView.as_view(template_name='index.html')),
    path('new-note/', TemplateView.as_view(template_name='index.html')),
    path('<int:id>/', TemplateView.as_view(template_name='index.html'))
]
