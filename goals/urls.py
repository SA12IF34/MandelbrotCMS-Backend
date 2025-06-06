from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('apis/goals/', views.GoalsAPIs.as_view(), name='goals_apis'),
    path('apis/goals/<int:pk>/', views.GoalAPIs.as_view(), name='goal_apis'),

    path('', TemplateView.as_view(template_name="index.html")),
    path('*', TemplateView.as_view(template_name="index.html"))

]

REACT_ROUTES = [
    'create-goal/',
    'goal/<int:id>/'
]

for route in REACT_ROUTES:
    urlpatterns.append(path(route, TemplateView.as_view(template_name="index.html")))