from django.conf.urls import include, url
import search.views as views

urlpatterns = [
    url(r'^search/$', views.SearchView.as_view(template_name='search.html'), name='search'),
    url(r'^search/(?P<page>\d+)/$', views.SearchView.as_view(template_name='search.html'), name='search'),

    url(r'^search/test/$', views.SearchView.as_view(template_name='search_test.html'), name='search_test'),
    url(r'^search/test/(?P<page>\d+)/$', views.SearchView.as_view(template_name='search_test.html'), name='search_test'),
]
