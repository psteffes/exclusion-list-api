from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    path('bruteforcelist/add/', views.add_key, name='add_key'),
    path('bruteforcelist/find/', views.find_key, name='find_key'),
    path('bruteforcelist/delete/', views.delete_key, name='delete_key'),
    path('umidexclist/find/', views.find_umid, name='find_umid'),
]
