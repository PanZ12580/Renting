from django.urls import path, re_path

from . import views

urlpatterns = [
    re_path(r'^login$', views.login),
    re_path(r'^findUserByToken$', views.findUserByToken),
    re_path(r'^findHouseList$', views.findHouseList),
    re_path(r'^removeHouse$', views.removeHouse),
    re_path(r'^getProxyList$', views.getProxyList),
    re_path(r'^getProxyCount$', views.getProxyCount),
    re_path(r'^removeProxy$', views.removeProxy),
    re_path(r'^getAvgRentBar$', views.getAvgRentBar),
    re_path(r'^getTagsCloud$', views.getTagsCloud),
    re_path(r'^getTypeNestedPie$', views.getTypeNestedPie),
    re_path(r'^getCostFunnel$', views.getCostFunnel),
    re_path(r'^getMultiPie$', views.getMultiPie),
    re_path(r'^getCostEffectiveLine$', views.getCostEffectiveLine),
    re_path(r'^getCostEffectiveBar$', views.getCostEffectiveBar),
    re_path(r'^getHeatmap$', views.getHeatmap),
]