from django.conf.urls import include, url
from content.views import StoryListView, StoryDetailView

urlpatterns = [
    url(r'^story/$', StoryListView.as_view(), name="story"),
    url(r'^story/(?P<slug>[\w-]+)/$', StoryDetailView.as_view(), name="story_detail"),
]
