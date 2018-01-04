from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^find/$', views.find, name='find'),
    url(r'^add/$', views.add, name='add'),
    url(r'^delete/$', views.delete, name='delete'),
]
