# app/urls.py

from django.conf.urls import url

from website import views

urlpatterns = [
  url(r'^$', views.index, name='index'),
  url(r'^profile/update', views.profile_update, name='profile_update'),
  url(r'^startup/update/$', views.startup_update, name='startup_update'),
  url(r'^profile/$', views.user_profile, name='profile'),
  url(r'^startup_profile/$', views.startup_profile, name='startup_profile'),
  url(r'^users/(?P<id>\d+)/$',views.get_user_view,name='get_user_view'),
  url(r'^connect/$', views.connect, name='connect'),
  url(r'^(?P<pk>\d+)/jobs/$', views.job_list, name='job_list'),
  url(r'^settings/$', views.Settings.as_view(), name='settings'),
  url(r'^settings/change_alternate_email/$', views.ChangeAlternateEmail.as_view(), name='change_alternate_email'),
]
