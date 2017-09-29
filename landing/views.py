from django.shortcuts import render
from django.views.generic.base import TemplateView, RedirectView
from django.core import urlresolvers
from website.views import index


# Create your views here.
def landing(request):
    if request.user.is_authenticated():
        return index(request)
    else:
        return render(request, 'index.html')
