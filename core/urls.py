from django.conf.urls import url
from metakill2 import settings
from . import views

urlpatterns = [
    url(r'^login/$', views.login),
    url(r'^$|^killer/$', views.list_killers),
    url(r'^killer/(?P<id>[0-9]+)/', views.view_killer, name='view_killer')
]
