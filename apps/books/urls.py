from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^login$', views.login),
    url(r'^register$', views.register),
    url(r'^logout$', views.logout),
    url(r'^books$', views.books),
    url(r'^books/add$', views.add),
    url(r'^books/(?P<id>\d+)$', views.book),
    url(r'^favorite/(?P<id>\d+)$', views.favorite),
    url(r'^unfavorite/(?P<id>\d+)$', views.unfavorite),
    url(r'^books/delete/(?P<id>\d+)$', views.delete),
    url(r'^books/update/(?P<id>\d+)$', views.update),
    url(r'^user', views.user),
    url(r'^', views.index),
]