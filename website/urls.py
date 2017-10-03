# app/urls.py

from django.conf.urls import url
from website import views


urlpatterns = [
  url(r'^search/$', views.search, name='search'),
  url(r'^search/(?P<category_search>\w+)/$', views.search, name='search'),
  url(r'^profile/update', views.profile_update, name='profile_update'),
  url(r'^startup/update/$', views.startup_update, name='startup_update'),
  url(r'^profile/$', views.user_profile, name='profile'),
  url(r'^startup_profile/$', views.startup_profile, name='startup_profile'),
  url(r'^profiles/(?P<id>\d+)/$',views.get_profile_view,name='get_profile_view'),
  url(r'^startups/(?P<id>\d+)/$',views.get_startup_view,name='get_startup_view'),
  url(r'^connect/$', views.connect, name='connect'),
  url(r'^(?P<pk>\d+)/jobs/$', views.job_list, name='job_list'),
  url(r'^settings/$', views.Settings.as_view(), name='settings'),
  # url(r'^settings/change_alternate_email/$', views.ChangeAlternateEmail.as_view(), name='change_alternate_email'),
  url(r'^settings/change_account_status/(?P<status>(enable|disable))$', views.ChangeAccountStatus.as_view(), name='change_account_status'),
  url(r'^resend/$', views.resend_activation_email, name='resend'),
  url(r'^settings/delete_profile/$', views.DeleteProfile.as_view(), name='delete_profile'),
  # url(r'^test/mail', views.test_mail, name='test_mail'),
]
