from django.conf.urls import include, url
import search.views as views

urlpatterns = [
    url(r'^search/(?P<page>\d+)/$', views.SearchView.as_view(), name='search'),
]
