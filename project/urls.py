from django.conf.urls import url, patterns
from django.contrib import admin

from kudryavka import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^admin/', admin.site.urls),
    url(r'^projects/$', views.project_index, name='projects'),
    url(r'^projects/(?P<project_id>[0-9]+)/$', views.project_view, name='notebook'),
]