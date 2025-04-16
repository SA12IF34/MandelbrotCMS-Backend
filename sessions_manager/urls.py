from django.urls import path
from django.views.generic import TemplateView
from .views import ProjectsAPIs, get_completed, get_in_progress, ProjectAPIs, PartitionAPIs

urlpatterns = [
    path('apis/projects/', ProjectsAPIs.as_view()),
    path('apis/projects/completed/', get_completed),
    path('apis/projects/in-progress/', get_in_progress),
    path('apis/projects/<int:id>/', ProjectAPIs.as_view()),
    path('apis/partitions/<int:id>/', PartitionAPIs.as_view()),

]
 