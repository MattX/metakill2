from django.conf.urls import url
from metakill2 import settings
from . import views

urlpatterns = [
    url(r'^login/$', views.login_view),
    url(r'^$|^killer/$', views.list_killers, name='list_killers'),
    url(r'^killer/(?P<id>[0-9]+)/', views.view_killer, name='view_killer'),
    url(r'^password/$', views.password_change, name='password_change'),
    url(r'^logout/$', views.logout_view, name='logout_view')
]
