from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from content.models import Story


# Create your views here.
class StoryListView(ListView):
    model = Story


class StoryDetailView(DetailView):
    model = Story