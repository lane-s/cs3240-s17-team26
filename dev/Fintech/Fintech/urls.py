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
from django.conf.urls import url, include
from django.contrib import admin
from Fintech import api, users, groups, reports, messages, search



urlpatterns = [
    url(r'^$', users.index, name='index'),
    url(r'^signup/$', users.signupform, name='signup'),
    url(r'^login/$',  auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^admin/', admin.site.urls, name='admin'),
    url(r'^groups/$', groups.viewGroups, name='groups'),
    url(r'^groups/new/$', groups.createGroup, name='createGroup'),
    url(r'^groups/(?P<pk>\d+)/leave/(?P<user_id>\d+)$', groups.leaveGroup, name='leaveGroup'),
    url(r'^groups/(?P<pk>\d+)/edit/$', groups.editGroup, name='editGroup'),
    url(r'^groups/(?P<pk>\d+)/delete/$', groups.deleteGroup, name='deleteGroup'),
    url(r'^groups/(?P<pk>\d+)/$', groups.viewGroup, name='viewGroup'),
    url(r'^reports/new/$', reports.createReport, name='createReport'),
    url(r'^reports/(?P<pk>\d+)/view/$', reports.viewReport, name='viewReport'),
    url(r'^reports/(?P<pk>\d+)/edit/$',reports.editReport, name='editReport'),
    url(r'^reports/(?P<pk>\d+)/delete/$',reports.deleteReport, name='deleteReport'),
    url(r'^search/?q=', search.search, name='searchReports'),
    url(r'^search/advanced/$', search.createAdvancedSearch, name='createAdvancedSearch'),
    url(r'^search/advanced/results/', search.advancedSearch, name='advancedSearchReports'),
    url(r'^messages/$', messages.viewMessages, name='viewMessages'),
    url(r'^messages/new/$', messages.sendMessage, name='sendMessage'),
    url(r'^messages/(?P<pk>\d+)/view/$', messages.viewMessage, name='viewMessage'),
    url(r'^messages/(?P<pk>\d+)/delete/$', messages.deleteMessage, name='deleteMessage'),
    url(r'^messages/(?P<pk>\d+)/decrypt/$', messages.decryptMessage, name='decryptMessage'),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/reports/$', api.ReportList.as_view()),
    url(r'^api/reports/(?P<reportID>\d+)/files/$', api.ReportFiles.as_view()),
    url(r'^settings/$', users.settings, name='settings'),
    url(r'^settings/password/$', users.change_password, name='change_password'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
