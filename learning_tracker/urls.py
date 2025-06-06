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
]
