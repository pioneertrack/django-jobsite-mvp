from django.conf.urls import include, url
from content.views import StoryListView, StoryDetailView

urlpatterns = [
    url(r'^stories/$', StoryListView.as_view(), name="stories"),
    url(r'^story/(?P<slug>[\w-]+)/$', StoryDetailView.as_view(), name="story_detail", ),
    # url(r'^content/images/(?P<slug>[\w-]+)/$', StoryDetailView.as_view(), name="story_detail"),
]
