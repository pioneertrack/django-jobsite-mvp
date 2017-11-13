from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from content.models import Story


# Create your views here.
class StoryListView(ListView):
    model = Story
    queryset = Story.objects.filter(published=True).order_by('-created_at')

class StoryDetailView(DetailView):
    model = Story