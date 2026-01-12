from django.urls import path
from . import views

urlpatterns = [
    path('', views.search_form, name='search_form'),
    path('start/', views.start_search, name='start_search'),
]
