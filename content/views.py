from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from search.views import JOB_CONTEXT
from content.models import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from website.decorators import check_profiles
from django.contrib.auth.decorators import user_passes_test
from django.utils.html import format_html
from dal import autocomplete


# Create your views here.
@method_decorator(check_profiles, 'get')
class StoryListView(LoginRequiredMixin, ListView):
    model = Story
    queryset = Story.objects.filter(published=True).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super(StoryListView, self).get_context_data(**kwargs)
        context.update(JOB_CONTEXT)
        return context


@method_decorator(check_profiles, 'get')
class StoryDetailView(LoginRequiredMixin, DetailView):
    model = Story

    def get_context_data(self, **kwargs):
        context = super(StoryDetailView, self).get_context_data(**kwargs)
        context.update(JOB_CONTEXT)
        return context


@method_decorator(check_profiles, 'get')
class ResourceListView(LoginRequiredMixin, ListView):
    model = Resource
    queryset = Resource.objects.filter(published=True).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super(ResourceListView, self).get_context_data(**kwargs)
        context.update(JOB_CONTEXT)
        return context


@method_decorator(check_profiles, 'get')
class ResourceDetailView(LoginRequiredMixin, DetailView):
    model = Resource

    def get_context_data(self, **kwargs):
        context = super(ResourceDetailView, self).get_context_data(**kwargs)
        context.update(JOB_CONTEXT)
        return context


@method_decorator(user_passes_test(lambda u: u.is_superuser), 'get')
class PictureAutocomplete(autocomplete.Select2QuerySetView):
    def get_result_label(self, item):
        # TODO TODO TODO PUT ESCAPING IN THIS WIDGET TO STOP XSS
        return format_html('<div class="auto-select"><div class="image-holder"><img src="{}"></div> {}</div>', item.image.url, item.title)

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Picture.objects.none()

        qs = Picture.objects.all()

        if self.q:
            qs = qs.filter(title__istartswith=self.q)

        return qs
