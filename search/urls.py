from django.conf.urls import include, url
import search.views as views

urlpatterns = [
    url(r'^new_search/(?P<page>\d+)/$', views.SearchView.as_view(), name='new_search'),
]
