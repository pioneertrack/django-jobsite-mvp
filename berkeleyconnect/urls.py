"""berkeleyconnect URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from registration.backends.hmac.views import RegistrationView
from django.conf.urls.static import static
from django.conf import settings


from website import forms
from website import views

urlpatterns = [
    url(r'^register/$',
        views.MyRegistrationView.as_view(
            form_class=forms.NewRegistrationForm
        ),
        name='registration_register',
    ),
    url(r'^logout/$',auth_views.logout_then_login, name = 'logout'),
    url(r'^password/reset/confirm/$', auth_views.password_reset_done, name = 'password_reset_done'),
    url(r'^password/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.password_reset_confirm, name = 'password_reset_confirm'),
    url(r'^password/reset/complete/$', auth_views.password_reset_complete, name = 'password_reset_complete'),
    url(r'^', include('registration.backends.hmac.urls')),
    url(r'^', include('website.urls')),
    url(r'^admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG and hasattr(settings, 'DEBUG_TOOLBAR_URLS'):
    urlpatterns = settings.DEBUG_TOOLBAR_URLS + urlpatterns