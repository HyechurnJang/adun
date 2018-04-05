"""adun URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
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
from django.conf.urls import url, include
from django.views.generic import RedirectView

import views

url_current = [
    url(r'^epg/', views.curr_epg, name='curr_epg'),
    url(r'^ep/', views.curr_ep, name='curr_ep'),
]

url_history = [
    url(r'^epg/', views.hist_epg, name='hist_epg'),
    url(r'^ep/', views.hist_ep, name='hist_ep'),
]

urlpatterns = [
    url(r'^favicon\.ico', RedirectView.as_view(url='/static/img/favicon.ico')),
    
    url(r'^current/', include(url_current)),
    url(r'^history/', include(url_history)),
    
    url(r'^hist/$', views.hist, name='hist'),
    
    url(r'^macip\.(?P<accept>json)/', views.macip, name='macip_json'),
    url(r'^macip/(?P<crud>\w+)/(?P<macip_id>\d+)?', views.macip, name='macip_crud'),
    url(r'^macip/$', views.macip, name='macip'),
    
    url(r'^', views.main, name='main'),
]
