from django.urls import path
from django.views.generic import TemplateView
from .views import (
    add_material_by_link,
    add_material_manually,
    get_all_materials,
    material_operations,
    get_special_materials,
    search_materials
)

urlpatterns = [
    path('apis/add/by-link/', add_material_by_link, name='add_material_by_link'),
    path('apis/add/manual/', add_material_manually, name='add_material_manually'),
    path('apis/all/', get_all_materials, name='get_all_materials'),
    path('apis/materials/<int:pk>/', material_operations, name='material_operations'),
    path('apis/special/', get_special_materials, name='get_special_materials'),
    path('apis/search/', search_materials, name='search_materials'),

    path('', TemplateView.as_view(template_name="index.html")),
    path('.*/', TemplateView.as_view(template_name="index.html"))
] 

REACT_ROUTES = [
    'add-material/',
    'materials/<int:id>/',
    'special/',
    'search/'
]

for route in REACT_ROUTES:
    urlpatterns.append(path(route, TemplateView.as_view(template_name="index.html")))