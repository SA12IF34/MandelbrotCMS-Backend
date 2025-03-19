from django.urls import path
from . import views

urlpatterns = [
    path('apis/goals/', views.GoalsAPIs.as_view(), name='goals_apis'),
    path('apis/goals/<int:pk>/', views.GoalAPIs.as_view(), name='goal_apis')
]