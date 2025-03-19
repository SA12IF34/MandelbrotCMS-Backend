from django.urls import path
from django.views.generic import TemplateView
from .views import (
    CoursesAPIs,
    CourseAPIs,
    update_section,
    get_course_data
)

urlpatterns = [
    path('apis/courses/', CoursesAPIs.as_view()),
    path('apis/courses/<int:pk>/', CourseAPIs.as_view()),
    path('apis/get-course-data/', get_course_data),
    path('apis/update-section/<int:pk>/', update_section),

    path('', TemplateView.as_view(template_name=''))
]

REACT_ROUTES = [
    'courses/<int:id>/',
    'add-course/',
]

for route in REACT_ROUTES:
    urlpatterns.append(path(route, TemplateView.as_view(template_name='')))