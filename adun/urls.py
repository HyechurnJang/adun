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

url_epg_detail = [
    url(r'^ep/(?P<ident>[\W\w]+)/', views.epg_ep, name='epg_ep'),
    url(r'^macip/(?P<ident>[\W\w]+)/(?P<crud>(create|read|update|delete))/', views.epg_macip, name='epg_macip'),
    url(r'^setting/', views.epg_setting, name='epg_setting')
]

url_detail = [
    url(r'^epg/', include(url_epg_detail)),
]

urlpatterns = [
    url(r'^favicon\.ico', RedirectView.as_view(url='/static/img/favicon.ico')),
    url(r'^topo/(?P<target>(epg|ep))/((?P<ident>[\W\w]+)/)?', views.topo, name='topo'),
    url(r'^detail/', include(url_detail)),
    url(r'^', views.main, name='main'),
]
