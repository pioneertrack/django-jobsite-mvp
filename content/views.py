from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from search.views import JOB_CONTEXT
from content.models import Story


# Create your views here.
class StoryListView(ListView):
    model = Story
    queryset = Story.objects.filter(published=True).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super(StoryListView, self).get_context_data(**kwargs)
        context.update(JOB_CONTEXT)
        return context

class StoryDetailView(DetailView):
    model = Story

    def get_context_data(self, **kwargs):
        context = super(StoryDetailView, self).get_context_data(**kwargs)
        context.update(JOB_CONTEXT)
        return context
