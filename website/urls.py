# app/urls.py

from django.conf.urls import url

from website import views

urlpatterns = [
  url(r'^$', views.index, name='index'),
  url(r'^profile/update', views.profile_update, name='profile_update'),
  url(r'^profile', views.profile, name='profile'),
  url(r'^users/(?P<id>\d+)/$',
                       views.get_user_view,
                       name='get_user_view'),
  url(r'^connect/$', views.connect, name='connect')
]
