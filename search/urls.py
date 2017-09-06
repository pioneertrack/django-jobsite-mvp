from django.conf.urls import include, url
import search.views as views

urlpatterns = [
    url(r'^search/$', views.SearchView.as_view(),name='search'),
]