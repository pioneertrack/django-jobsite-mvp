from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from search.views import JOB_CONTEXT
from content.models import Story
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from website.decorators import check_profiles


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
