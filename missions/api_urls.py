from django.urls import path
from . import views
 
urlpatterns = [
    path('apis/lists/', views.ListsAPIs.as_view(), name='lists_apis'),
    path('apis/lists/today/<str:date>/', views.get_today_list, name='get_today_list'),
    path('apis/lists/<int:pk>/', views.ListAPIs.as_view(), name='list_apis'),
    path('apis/missions/<int:pk>/', views.mission_operations, name='mission_operations'),
    path('apis/lists/<int:pk>/<str:sequence>/', views.get_sequence_list, name='get_sequence_list'),
    path('apis/set-cookie/', views.set_cookie, name="set_cookie")
]