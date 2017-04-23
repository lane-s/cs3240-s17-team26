"""Fintech URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
import django
django.setup()

from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from Fintech import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^signup/$', views.signupform, name='signup'),
    url(r'^login/$',  auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^admin/', admin.site.urls, name='admin'),
    url(r'^groups/$', views.viewGroups, name='groups'),
    url(r'^groups/new/$', views.createGroup, name='createGroup'),
    url(r'^groups/(?P<pk>\d+)/leave/(?P<user_id>\d+)$', views.leaveGroup, name='leaveGroup'),
    url(r'^groups/(?P<pk>\d+)/edit/$', views.editGroup, name='editGroup'),
    url(r'^groups/(?P<pk>\d+)/delete/$', views.deleteGroup, name='deleteGroup'),
    url(r'^groups/(?P<pk>\d+)/$', views.viewGroup, name='viewGroup'),
    url(r'^reports/new/$', views.createReport, name='createReport'),
    url(r'^reports/(?P<pk>\d+)/view/$', views.viewReport, name='viewReport'),
    url(r'^reports/(?P<pk>\d+)/edit/$',views.editReport, name='editReport'),
    url(r'^reports/(?P<pk>\d+)/delete/$',views.deleteReport, name='deleteReport'),
    url(r'^search/?q=', views.search, name='searchReports'),
    url(r'^search/advanced/$', views.createAdvancedSearch, name='createAdvancedSearch'),
    url(r'^search/advanced/?fields=/?values=/$', views.advancedSearch, name='advancedSearchReports'),
    url(r'^messages/$', views.viewMessages, name='viewMessages'),
    url(r'^messages/new/$', views.sendMessage, name='sendMessage'),
    url(r'^messages/(?P<pk>\d+)/view/$', views.viewMessage, name='viewMessage'),
    url(r'^messages/(?P<pk>\d+)/delete/$', views.deleteMessage, name='deleteMessage'),
    url(r'^messages/(?P<pk>\d+)/decrypt/$', views.decryptMessage, name='decryptMessage'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
