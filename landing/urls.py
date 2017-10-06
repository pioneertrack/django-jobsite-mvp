from django.views.generic.base import TemplateView
from django.conf.urls import include, url
from landing.views import landing

urlpatterns = [
    url(r'^$', landing, name="home"),
]
